"""
object_detection.py — Entry point for the Object Detection System.

Two ways to run:
  1. Interactive menu (no arguments):   python src/object_detection.py
     - The pretrained model loads ONCE per session, then the menu
       reappears after every detection, so many predictions can be
       run without restarting the program.
  2. Command-line arguments, e.g.:
       python src/object_detection.py --mode image --source data/input/images/street.jpg
       python src/object_detection.py --mode video --source data/input/videos/traffic.mp4
       python src/object_detection.py --mode webcam
     Options: --conf 0.4   --model yolo11n.pt   --device cpu|0   --no-preview
     (CLI mode runs ONE detection, then exits.)

Controls:  Q exits video/webcam mode · S saves a webcam snapshot ·
any key closes the image preview.

Internship : AI/ML Internship — RaushByte Technologies (Level 3, Task 2)
"""

import argparse

from config import (CAMERA_INDEX, CONFIDENCE_THRESHOLD, DEVICE,
                    INPUT_IMAGES_DIR, INPUT_VIDEOS_DIR, MODEL_PATH,
                    SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS)
from detector import detect_image, detect_video, detect_webcam, load_model
from utils import ensure_directories

BANNER = """
====================================================
        REAL-TIME OBJECT DETECTION SYSTEM
      YOLO + Python | RaushByte Technologies
====================================================
"""


def parse_args():
    """Command-line arguments (all optional — menu runs when omitted)."""
    parser = argparse.ArgumentParser(
        description="Real-Time Object Detection System using YOLO and Python")
    parser.add_argument("--mode", choices=["image", "video", "webcam"],
                        help="detection mode (omit for the interactive menu)")
    parser.add_argument("--source",
                        help="path to the input image or video file")
    parser.add_argument("--conf", type=float,
                        help=f"confidence threshold 0-1 "
                             f"(default: {CONFIDENCE_THRESHOLD})")
    parser.add_argument("--model", default=MODEL_PATH,
                        help=f"pretrained YOLO model (default: {MODEL_PATH})")
    parser.add_argument("--device", default=DEVICE,
                        help=f"'cpu' or a GPU index like 0 (default: {DEVICE})")
    parser.add_argument("--no-preview", action="store_true",
                        help="image mode only: skip the preview window")
    return parser.parse_args()


def ask_for_source(kind: str) -> str:
    """Ask for an input file, offering files already in the project folders."""
    folder = INPUT_IMAGES_DIR if kind == "image" else INPUT_VIDEOS_DIR
    extensions = (SUPPORTED_IMAGE_FORMATS if kind == "image"
                  else SUPPORTED_VIDEO_FORMATS)
    files = (sorted(p for p in folder.iterdir()
                    if p.suffix.lower() in extensions)
             if folder.exists() else [])

    if files:
        print(f"\nFiles found in {folder}:")
        for index, file in enumerate(files, start=1):
            print(f"  {index}. {file.name}")
        choice = input("Enter a number, or type a full file path: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return str(files[int(choice) - 1])
        return choice
    return input(f"Enter the path to the {kind} file: ").strip()


def interactive_menu():
    """Console menu — returns (mode, source), or (None, None) to exit."""
    print("Select Detection Mode:\n")
    print("  1. Image Detection")
    print("  2. Video Detection")
    print("  3. Webcam Detection")
    print("  4. Exit\n")
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            return "image", ask_for_source("image")
        if choice == "2":
            return "video", ask_for_source("video")
        if choice == "3":
            return "webcam", None
        if choice == "4":
            return None, None
        print("Invalid choice — please enter 1, 2, 3 or 4.")


# ------------------------------------------------------------------
# Model cache — load the pretrained YOLO model only ONCE per program
# run, then reuse it for every detection. (Reloading the model before
# each detection would make the menu loop painfully slow.)
# ------------------------------------------------------------------

_loaded_model = None


def get_model(args):
    """Load the pretrained model on first use; reuse it afterwards.

    Returns the loaded YOLO model, or None if loading failed (the
    error message is printed here so callers only check for None).
    """
    global _loaded_model
    if _loaded_model is None:
        try:
            _loaded_model = load_model(args.model, args.device)
        except RuntimeError as error:
            print(f"Error: {error}")
            return None
    return _loaded_model


# ------------------------------------------------------------------
# Single detection run (shared by CLI mode and the menu loop)
# ------------------------------------------------------------------

def run_detection(mode, source, conf, args):
    """Run ONE detection (image / video / webcam) with friendly errors.

    Errors (bad path, missing camera, ...) are handled here so that in
    menu mode the user returns to the menu instead of the app crashing.
    """
    # In CLI mode the --source argument may be missing — ask for it
    if mode in ("image", "video") and not source:
        source = ask_for_source(mode)
    if mode in ("image", "video") and not source:
        print("Error: no input file was provided.")
        return

    model = get_model(args)
    if model is None:
        return                      # the load error was already printed

    try:
        if mode == "image":
            detect_image(model, source, conf, args.device,
                         show_preview=not args.no_preview)
        elif mode == "video":
            detect_video(model, source, conf, args.device)
        else:
            detect_webcam(model, conf, camera_index=CAMERA_INDEX,
                          device=args.device)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"Error: {error}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")


# ------------------------------------------------------------------
# Main application
# ------------------------------------------------------------------

def main():
    args = parse_args()
    print(BANNER)
    ensure_directories()

    # Validate the confidence threshold once, up front
    # (must be strictly between 0 and 1)
    conf = args.conf if args.conf is not None else CONFIDENCE_THRESHOLD
    if not 0.0 < conf < 1.0:
        print(f"Error: the confidence threshold must be between 0 and 1 "
              f"(got {conf}).")
        return

    # --- CLI mode (--mode given): run one detection, then exit ------
    if args.mode:
        run_detection(args.mode, args.source, conf, args)
        return

    # --- Menu mode: after each detection, come BACK to the menu -----
    # The model loads on the FIRST detection only (see get_model) and
    # is reused for every subsequent detection in the same session.
    try:
        while True:
            mode, source = interactive_menu()
            if mode is None:
                print("Goodbye!")
                return
            run_detection(mode, source, conf, args)
    except KeyboardInterrupt:
        # Ctrl+C at the menu prompt (or Ctrl+C twice) — exit cleanly
        print("\nInterrupted by user. Goodbye!")


if __name__ == "__main__":
    main()