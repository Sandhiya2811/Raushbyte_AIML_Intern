import os
import time

import cv2

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

WINDOW_NAME = "Real-Time Face Detection"
CASCADE_FILE = "haarcascade_frontalface_default.xml"

# Bounding box style (color is BGR in OpenCV)
BOX_COLOR = (255, 0, 0)     # blue boxes, as required by the task spec
BOX_THICKNESS = 2
LABEL_TEXT = "Face"

# On-screen text style
FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_COLOR = (0, 255, 0)    # green overlays

# Detection parameters (explained in docs/project_report.md, Section 5)
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_FACE_SIZE = (30, 30)


# ------------------------------------------------------------------
# 1. Loading the face detector
# ------------------------------------------------------------------

def load_face_detector():
    """
    Load OpenCV's pretrained Haar Cascade frontal-face classifier.

    Returns the loaded classifier on success, or None if loading failed
    (e.g., a broken/incomplete OpenCV installation).
    """
    # cv2.data.haarcascades is the built-in folder of pretrained
    # cascade XML files that ships with OpenCV - no download needed.
    cascade_path = cv2.data.haarcascades + CASCADE_FILE
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # NOTE: CascadeClassifier() never returns None on failure -
    # it returns an EMPTY classifier. So the correct check is .empty().
    if face_cascade.empty():
        print("Error: Could not load the Haar Cascade classifier file.")
        print("Attempted path:", cascade_path)
        print("Try reinstalling OpenCV:")
        print("    python -m pip install --upgrade opencv-python")
        return None

    return face_cascade


# ------------------------------------------------------------------
# 2. Detecting faces in a frame
# ------------------------------------------------------------------

def detect_faces(frame, face_cascade):
    """
    Detect human faces in a single video frame.

    Steps:
      1. Convert the frame to grayscale. Haar Cascades are trained on
         grayscale images, and grayscale (1 channel) is about 3x less
         data to scan than color (3 channels) - so detection is faster.
      2. Run the multi-scale Haar Cascade detector.

    Returns an array of face locations as (x, y, w, h) rectangles
    (empty if no faces are found).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=SCALE_FACTOR,      # image shrink step per scan pass
        minNeighbors=MIN_NEIGHBORS,    # required overlapping detections
        minSize=MIN_FACE_SIZE,         # ignore anything smaller than this
    )
    return faces


# ------------------------------------------------------------------
# 3. Drawing the results on the frame
# ------------------------------------------------------------------

def draw_results(frame, faces):
    """
    Draw a bounding box and a "Face" label around every detected face.
    The frame is modified in place and also returned for convenience.
    """
    for (x, y, w, h) in faces:
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv2.rectangle(frame, top_left, bottom_right, BOX_COLOR, BOX_THICKNESS)

        # Label just above the box (kept on-screen if the face is
        # at the very top of the frame)
        label_position = (x, max(y - 10, 12))
        cv2.putText(frame, LABEL_TEXT, label_position,
                    FONT, 0.6, BOX_COLOR, BOX_THICKNESS)

    return frame


# ------------------------------------------------------------------
# 4. Main application
# ------------------------------------------------------------------

def main():
    """Run the real-time face detection loop until the user presses Q."""
    # --- Load the face detector --------------------------------
    face_cascade = load_face_detector()
    if face_cascade is None:
        return  # error message already printed

    # --- Open the webcam ---------------------------------------
    cap = cv2.VideoCapture(0)  # 0 = default webcam

    if not cap.isOpened():
        print("Unable to access the webcam.")
        print("Please check camera permissions and connection.")
        return

    print(WINDOW_NAME, "running...")
    print("Press Q to exit, S to save a screenshot.")

    # For the live FPS counter (optional enhancement)
    previous_frame_time = time.time()

    # try/finally guarantees the camera is ALWAYS released,
    # even if an unexpected error (or Ctrl+C) occurs.
    try:
        while True:
            # 1. Capture one frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Failed to read a frame from the webcam. Exiting.")
                break

            # 2. Detect faces in the frame
            faces = detect_faces(frame, face_cascade)

            # 3. Draw bounding boxes and labels
            draw_results(frame, faces)

            # 4. Overlay: face count (top-left), exit hint (bottom-left),
            #    FPS (top-right)
            frame_height, frame_width = frame.shape[:2]

            cv2.putText(frame, f"Faces Detected: {len(faces)}",
                        (10, 30), FONT, 0.8, TEXT_COLOR, 2)
            cv2.putText(frame, "Press Q to Exit",
                        (10, frame_height - 15), FONT, 0.6, TEXT_COLOR, 2)

            # Optional enhancement: live FPS counter
            current_time = time.time()
            if current_time > previous_frame_time:
                fps = 1.0 / (current_time - previous_frame_time)
            else:
                fps = 0
            previous_frame_time = current_time
            cv2.putText(frame, f"FPS: {int(fps)}",
                        (frame_width - 100, 30), FONT, 0.7, (0, 255, 255), 2)

            # 5. Show the processed frame
            cv2.imshow(WINDOW_NAME, frame)

            # 6. Keyboard input (wait 1 ms per frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == ord("Q"):
                break  # exit -> cleanup in finally block

            # Optional enhancement: S saves the current annotated frame
            if key == ord("s") or key == ord("S"):
                os.makedirs("screenshots", exist_ok=True)
                filename = os.path.join(
                    "screenshots", f"capture_{int(time.time())}.png")
                if cv2.imwrite(filename, frame):
                    print("Screenshot saved:", filename)

    finally:
        # 7. Release resources - always runs
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam released. Application closed.")


if __name__ == "__main__":
    main()