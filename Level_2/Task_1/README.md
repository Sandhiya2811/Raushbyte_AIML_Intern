# Real-Time Face Detection System using OpenCV and Python

A beginner-friendly, real-time face detection application developed as part of the **RaushByte Technologies AI/ML Internship**.

**Internship:** AI/ML Internship – RaushByte Technologies
**Task:** Level 2 – Task 1: Face Detection
**Prepared By:** Sandhiya

> ⚠️ **Scope note:** This project performs **face detection only** — it finds *where* faces are in a live webcam feed. It does **not** perform face recognition (identifying *who* a face belongs to).

## Objective

Build a real-time application that:

* Accesses the computer webcam
* Captures and processes live video frames
* Detects human faces using a Haar Cascade classifier
* Draws bounding boxes around every detected face
* Displays a live count of detected faces
* Exits safely when the user presses **Q**

## Features

* Real-time webcam input
* Face detection using a pretrained Haar Cascade classifier
* Grayscale preprocessing for faster detection
* Bounding boxes with `"Face"` labels
* Live face counter (e.g., `Faces Detected: 2`)
* Live FPS counter *(optional enhancement)*
* Screenshot capture with the **S** key *(optional enhancement)*
* Keyboard exit (**Q**)
* Error handling for webcam access and classifier loading
* Proper resource cleanup (camera always released)

## Tech Stack

**Python | OpenCV | Haar Cascade Classifier**

## Installation

1. Install **Python 3.8+** from [**https://www.python.org/downloads/**](https://www.python.org/downloads/).

   > On Windows, tick **"Add Python to PATH"** during installation.

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

   Only `opencv-python` is required. No APIs, cloud services, or GPU are needed.

## How to Run

From the **project root** folder:

```powershell
python src/face_detection.py
```

> Run from the project root (not from inside `src/`) so that screenshots saved with the **S** key go into the project's `screenshots/` folder.

The webcam window should open, showing the live feed with detection results.

| **Key** | **Action**                                     |
| ------- | ---------------------------------------------- |
| **Q**   | Exit the application                           |
| **S**   | Save an annotated screenshot to `screenshots/` |

## How It Works

```text
Webcam
   ↓
Video Frame
   ↓
Grayscale Conversion
   ↓
Haar Cascade
   ↓
Face Detection
   ↓
Bounding Boxes
   ↓
Face Count
   ↓
Display
```

| **Stage**                | **What happens**                                                                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Webcam**               | `cv2.VideoCapture(0)` opens the default camera.                                                                                                         |
| **Video Frame**          | `cap.read()` grabs one image at a time (webcams typically provide ~30 frames per second).                                                               |
| **Grayscale Conversion** | `cv2.cvtColor(...)` converts each frame to grayscale — cascades are trained on grayscale, and 1 channel is ~3× less data to scan than 3 color channels. |
| **Haar Cascade**         | `detectMultiScale()` scans the image at multiple sizes, looking for face patterns.                                                                      |
| **Face Detection**       | Returns each face's location as `(x, y, w, h)`.                                                                                                         |
| **Bounding Boxes**       | `cv2.rectangle()` draws a blue box around each face; each is labeled `"Face"`.                                                                          |
| **Face Count**           | `len(faces)` is displayed live on the window.                                                                                                           |
| **Display**              | `cv2.imshow()` shows the annotated frame; the loop repeats until **Q** is pressed.                                                                      |

## Detection Parameters

| **Parameter**  |  **Value** | **Purpose**                                                                                                        |
| -------------- | ---------: | ------------------------------------------------------------------------------------------------------------------ |
| `scaleFactor`  |      `1.1` | How much the image is shrunk at each scan step (1.1 = 10%). Smaller = more thorough but slower.                    |
| `minNeighbors` |        `5` | How many overlapping detections a candidate region needs to be accepted as a face. Higher = fewer false positives. |
| `minSize`      | `(30, 30)` | Minimum face size to detect — filters out tiny false positives and speeds up scanning.                             |

## Project Structure

```text
raushbyte-face-detection/
│
├── README.md
├── src/
│   └── face_detection.py
├── requirements.txt
├── screenshots/
│   └── face_detection_demo.png
└── docs/
    └── project_report.md
```

## Limitations

* Lighting conditions affect detection (low light reduces accuracy).
* Side-facing or strongly tilted faces are harder to detect (this cascade is trained mainly on **frontal** faces).
* Occlusion (hand over face, mask, glasses glare) reduces detection.
* Occasional false positives can occur.
* Haar Cascade is less robust than modern deep-learning detectors.
* The system detects faces only — it does **not** identify people.

## Troubleshooting

| **Problem**                                  | **Fix**                                                                                                                                                                                                                                                                                 |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Unable to access the webcam.`               | Check camera permissions (Windows: Settings → Privacy → Camera; macOS: System Settings → Privacy & Security → Camera, allow your terminal/IDE). Close Zoom/Teams/other apps using the camera. If using an external webcam, try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`. |
| `ModuleNotFoundError: No module named 'cv2'` | Run `python -m pip install opencv-python` (use `py -m pip ...` on Windows if needed).                                                                                                                                                                                                   |
| Classifier load error                        | Reinstall: `python -m pip install --upgrade opencv-python`                                                                                                                                                                                                                              |
| Q doesn't exit                               | The OpenCV window must be the **active/focused** window when you press **Q**.                                                                                                                                                                                                           |

## Privacy Note

This application processes video **entirely on your local machine**. No frames are uploaded, stored, or transmitted anywhere. Frames are kept only in memory and discarded; the only saved image is one you explicitly create by pressing **S**.

Always use a webcam with the knowledge and consent of anyone in the frame.

## Future Enhancements (not implemented in this task)

* Deep-learning-based face detection (e.g., OpenCV DNN module, MediaPipe, YOLO-based detectors)
* Improved robustness under poor lighting (e.g., histogram equalization)
* Better handling of non-frontal face angles
* Face landmark detection
* Performance optimization
* Optional graphical interface

## Acknowledgment

Developed as part of the **AI/ML Internship at RaushByte Technologies** (Level 2 – Task 1).

Thank you for the opportunity to apply **Computer Vision fundamentals** hands-on.
