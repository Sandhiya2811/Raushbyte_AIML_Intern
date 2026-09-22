import datetime
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

from config import (CAMERA_INDEX, OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR,
                    SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS)
from utils import (FpsMeter, count_objects, detections_summary,
                   draw_detections, overlay_stats, save_image)


# ------------------------------------------------------------------
# Model loading
# ------------------------------------------------------------------

def load_model(model_path: str, device: str = "cpu") -> YOLO:
    """Load a pretrained YOLO model (auto-downloads on first run)."""
    if not Path(model_path).exists():
        print(f"Note: '{model_path}' not found locally — it will be")
        print("downloaded automatically from Ultralytics on first use")
        print("(internet required once; the file is then cached).\n")
    try:
        model = YOLO(model_path)
    except Exception:
        raise RuntimeError(
            f"Could not load or download the model '{model_path}'. "
            "Check your internet connection (needed for the first-run "
            "download) and the model name — see the available models at "
            "https://docs.ultralytics.com/models")
    print(f"Model loaded: '{model_path}' — {len(model.names)} object "
          f"classes (device: {device})")
    return model


def _resolve_device(device):
    """Normalize the device setting: 'cpu'/'cuda:0' pass through,
    a numeric string like '0' becomes an int GPU index."""
    text = str(device).strip()
    if text.lstrip("-").isdigit():
        return int(text)
    return text or "cpu"


def run_inference(model, frame, conf_threshold: float, device: str = "cpu"):
    """Run YOLO inference on one frame (the spec's 'process_frame')."""
    return model.predict(frame, conf=conf_threshold,
                         device=_resolve_device(device), verbose=False)


# ------------------------------------------------------------------
# Mode 1 — Image detection
# ------------------------------------------------------------------

def detect_image(model, image_path, conf_threshold: float,
                 device: str = "cpu", show_preview: bool = True):
    """Detect objects in one image, save and (optionally) show the result."""
    path = Path(image_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: '{path}'")
    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(
            f"Unsupported image format '{path.suffix}'. Supported: "
            f"{', '.join(sorted(SUPPORTED_IMAGE_FORMATS))}")

    frame = cv2.imread(str(path))
    if frame is None:
        raise ValueError("The image could not be opened — it may be "
                         "corrupted or in an unsupported format.")

    results = run_inference(model, frame, conf_threshold, device)
    annotated = draw_detections(frame, results)
    total, per_class = count_objects(results)
    overlay_stats(annotated, total, per_class)

    print(f"\nInput image : {path.name}")
    summary = detections_summary(results)
    if summary:
        print("Detected objects:")
        for line in summary:
            print(f"  {line}")
    else:
        print(f"No objects detected above the confidence threshold "
              f"({conf_threshold:.2f}).")
    print(f"Objects Detected: {total}")

    output_path = OUTPUT_IMAGES_DIR / f"{path.stem}_detected.jpg"
    if save_image(annotated, output_path):
        print(f"Annotated image saved to: {output_path}")
    else:
        print("Warning: the annotated image could not be saved.")

    if show_preview:
        cv2.imshow("Image Detection — press any key to close", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return output_path


# ------------------------------------------------------------------
# Mode 2 — Video detection (sequential frames, never whole-file loading)
# ------------------------------------------------------------------

def detect_video(model, video_path, conf_threshold: float, device: str = "cpu"):
    """Detect objects frame by frame and write the annotated video."""
    path = Path(video_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Video not found: '{path}'")
    if path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        raise ValueError(
            f"Unsupported video format '{path.suffix}'. Supported: "
            f"{', '.join(sorted(SUPPORTED_VIDEO_FORMATS))}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open the video '{path.name}'. The "
                           "file may be corrupted or the codec unsupported.")

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    if not source_fps or source_fps != source_fps:      # 0 or NaN
        source_fps = 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Output writer — with an AVI/XVID fallback if MP4 encoding fails
    output_path = OUTPUT_VIDEOS_DIR / f"{path.stem}_detected.mp4"
    OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path),
                             cv2.VideoWriter_fourcc(*"mp4v"),
                             source_fps, (width, height))
    if not writer.isOpened():
        output_path = OUTPUT_VIDEOS_DIR / f"{path.stem}_detected.avi"
        writer = cv2.VideoWriter(str(output_path),
                                 cv2.VideoWriter_fourcc(*"XVID"),
                                 source_fps, (width, height))
    if not writer.isOpened():
        print("Warning: could not create the output video file — "
              "continuing with preview only.")

    print(f"\nProcessing video: {path.name}")
    if total_frames > 0:
        print(f"Frames: {total_frames} | Resolution: {width}x{height}")
    print("Press Q in the preview window to stop early.\n")

    meter = FpsMeter()
    start_time = time.perf_counter()
    frames_processed = 0

    try:
        while True:
            ret, frame = cap.read()          # one frame at a time —
            if not ret:                      # the video is NEVER fully
                break                        # loaded into memory

            results = run_inference(model, frame, conf_threshold, device)
            annotated = draw_detections(frame, results)
            total, per_class = count_objects(results)
            fps = meter.update()
            overlay_stats(annotated, total, per_class, fps)
            frames_processed += 1

            if writer.isOpened():
                writer.write(annotated)

            cv2.imshow("Video Detection — press Q to stop", annotated)
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), ord("Q")):
                print("\nStopped early by user.")
                break
            if total_frames > 0 and frames_processed % 50 == 0:
                percent = 100 * frames_processed / total_frames
                print(f"  Processed {frames_processed}/{total_frames} "
                      f"frames ({percent:.0f}%)")
    finally:
        cap.release()
        wrote_video = writer.isOpened()
        if wrote_video:
            writer.release()
        cv2.destroyAllWindows()

    elapsed = time.perf_counter() - start_time
    if frames_processed > 0 and elapsed > 0:
        print(f"\nDone. {frames_processed} frame(s) processed at an average "
              f"of {frames_processed / elapsed:.1f} FPS (processing speed).")
    if wrote_video:
        print(f"Annotated video saved to: {output_path}")
    else:
        print("No output video was written (writer unavailable).")
    return output_path


# ------------------------------------------------------------------
# Mode 3 — Real-time webcam detection
# ------------------------------------------------------------------

def detect_webcam(model, conf_threshold: float,
                  camera_index: int = CAMERA_INDEX, device: str = "cpu"):
    """Real-time detection on the live webcam feed (Q = exit, S = snapshot)."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Unable to open the webcam. Please check whether "
                           "another application is using the camera, and "
                           "that camera permissions are enabled.")

    print(f"\nWebcam started (camera index {camera_index}).")
    print("Press Q to exit — S saves a snapshot of the annotated frame.")

    meter = FpsMeter()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read a frame from the webcam. Exiting.")
                break

            results = run_inference(model, frame, conf_threshold, device)
            annotated = draw_detections(frame, results)
            total, per_class = count_objects(results)
            fps = meter.update()
            overlay_stats(annotated, total, per_class, fps)

            cv2.imshow("Webcam Detection — press Q to exit", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q")):
                break
            if key in (ord("s"), ord("S")):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
                snapshot = OUTPUT_IMAGES_DIR / f"webcam_capture_{timestamp}.jpg"
                if save_image(annotated, snapshot):
                    print(f"Snapshot saved: {snapshot.name}")
                else:
                    print("Warning: snapshot could not be saved.")
    finally:
        cap.release()                      # camera ALWAYS released
        cv2.destroyAllWindows()
        print("Webcam released — camera closed.")