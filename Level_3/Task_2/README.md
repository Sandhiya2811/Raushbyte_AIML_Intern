# Real-Time Object Detection System using YOLO and Python

**Computer Vision Application for Detecting Objects in Images, Videos, and Webcam Streams**

**Internship:** AI/ML Internship – RaushByte Technologies
**Task:** Level 3 – Task 2: Computer Vision Project
**Prepared By:** Sandhiya

---

## Overview

This project is a **pretrained YOLO object detection system** built with Python, Ultralytics YOLO, and OpenCV.

It detects **multiple everyday objects** in three modes:

* Images
* Video files
* Live webcam streams

The system draws **bounding boxes, class labels, and confidence scores**, counts objects per frame, displays FPS for streams, and saves annotated results.

> **Accurate description:** This project performs **pretrained object detection using inference** (transfer of an already-trained model). **No custom training** is performed. It is **object detection**, not face recognition or person identification.

### Progression from Level 2

My earlier Level 2 face-detection task used a classical Haar Cascade. This project upgrades the approach to a modern **deep-learning object detector**.

| Feature               | Level 2 – Haar Cascade                              | Level 3 – YOLO                          |
| --------------------- | --------------------------------------------------- | --------------------------------------- |
| Approach              | Classical computer vision / cascade-based detection | Deep learning / single-stage CNN        |
| Detects               | Frontal faces                                       | 80 COCO object classes                  |
| Confidence scores     | No                                                  | Yes, per detection                      |
| Multiple object types | No                                                  | Yes, simultaneously                     |
| Example objects       | Faces                                               | Person, car, dog, laptop, bicycle, etc. |

---

## Objective

Object detection answers two questions at once:

1. **What** is in the image — classification
2. **Where** is it — localization using a bounding box

Automated object detection is useful for:

* Counting objects
* Monitoring
* Accessibility applications
* Computer vision systems
* Tracking foundations
* Segmentation systems

This project demonstrates the complete detection pipeline:

**Model Loading → Inference → Post-Filtering → Visualization → Result Saving**

The pipeline works across static images, video files, and live webcam input.

---

## Features

* Image detection with bounding boxes, labels, confidence scores, and object counts
* Video detection frame-by-frame
* Sequential video processing without loading the entire video into memory
* Real-time webcam detection
* `Q` key to exit video/webcam mode
* `S` key to save a webcam snapshot
* Configurable confidence threshold
* Per-frame object counting
* Per-class object counting
* Approximate FPS display for video and webcam streams
* Automatic first-run model download
* CPU support by default
* Optional GPU configuration using `DEVICE=0`
* Interactive menu
* Command-line interface
* Friendly error handling for invalid paths, corrupted files, missing cameras, etc.

---

## Architecture

```text
Input
(image / video frame / webcam frame)
        ↓
Preprocessing
(resize + normalization inside model.predict)
        ↓
YOLO Model
(pretrained single-stage CNN)
        ↓
Inference
(one forward pass)
        ↓
Post-processing
(confidence filtering + NMS inside the library)
        ↓
Bounding Boxes
+ Class Names
+ Confidence Scores
        ↓
Drawing & Counting
(our OpenCV code: boxes, labels, statistics, FPS)
        ↓
Output
(annotated image / video / live window)
```

### Image Workflow

```text
Input Image
    ↓
YOLO
    ↓
Detection
    ↓
Bounding Boxes
    ↓
Class + Confidence
    ↓
Annotated Image
    ↓
data/output/images/
```

### Video Workflow

```text
Video
    ↓
Frame Extraction
(sequential)
    ↓
YOLO Inference
    ↓
Annotation
    ↓
Output Video
data/output/videos/
```

### Webcam Workflow

```text
Webcam
    ↓
Frame Capture
    ↓
YOLO Inference
    ↓
Bounding Boxes
    ↓
Display
    ↓
Next Frame
    ↓
Q exits
```

The camera is always released when webcam processing ends.

---

## Technologies

| Technology                    | Purpose                                                   |
| ----------------------------- | --------------------------------------------------------- |
| **Python 3**                  | Core programming language                                 |
| **Ultralytics YOLO (YOLO11)** | Pretrained object detection model and inference API       |
| **OpenCV**                    | Image/video reading, drawing, writing, and webcam capture |
| **NumPy**                     | Array and image mathematics used by OpenCV/YOLO           |
| **PyTorch**                   | Deep-learning backend used by YOLO                        |

---

## Requirements

* Python 3.8+
* Internet connection **once** for downloading the pretrained model
* Webcam for webcam mode
* No GPU required
* CPU works by default

---

## Installation

From the `Task_2` folder in PowerShell:

### 1. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

If activation is blocked by PowerShell's execution policy, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This changes the policy for the current user and does not require administrator rights.

Alternatively, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

> **Note:** `pip install ultralytics` automatically installs the required PyTorch dependency. If you have a CUDA-compatible GPU and want GPU acceleration, install an appropriate GPU-enabled PyTorch build according to the PyTorch documentation, then set `DEVICE=0`.

---

## Running the Project

### Interactive Menu

The interactive menu is recommended because it does not require memorizing command-line arguments.

```powershell
python src/object_detection.py
```

### Command-Line Mode

#### Image Detection

```powershell
python src/object_detection.py --mode image --source data/input/images/street.jpg
```

#### Video Detection

```powershell
python src/object_detection.py --mode video --source data/input/videos/traffic.mp4
```

#### Webcam Detection

```powershell
python src/object_detection.py --mode webcam
```

#### Webcam with Custom Confidence and GPU

```powershell
python src/object_detection.py --mode webcam --conf 0.5 --device 0
```

### Controls

| Key     | Action                  |
| ------- | ----------------------- |
| `Q`     | Exit video/webcam mode  |
| `S`     | Save a webcam snapshot  |
| Any key | Close the image preview |

---

## Model

### Model Information

* **Model:** `yolo11n.pt`
* **Variant:** Nano — small and fast YOLO11 model
* **Source:** Ultralytics
* **Training Dataset:** COCO
* **Number of COCO Classes:** 80
* **Usage:** Inference only

The model is **pretrained** and is automatically downloaded on the first run.

The `.pt` model file is downloaded into the directory from which the command is executed, depending on the Ultralytics configuration/version.

> If your installed Ultralytics version uses older model naming, `yolov8n.pt` may also be used. The inference API is similar, but the exact model behavior and supported features can differ by model/version.

For official model information, refer to the [Ultralytics documentation](https://docs.ultralytics.com/models).

### Training Status

This project **does not**:

* Train the YOLO model
* Fine-tune the model
* Modify the pretrained weights
* Use a custom training dataset

The project only performs **inference using a pretrained model**.

---

## Supported Classes

The model can detect categories present in its COCO training data.

Examples include:

* Person
* Car
* Bicycle
* Bus
* Truck
* Dog
* Cat
* Bottle
* Chair
* Laptop
* Cellphone
* Backpack

The model cannot detect arbitrary objects outside its supported classes.

It also does **not identify who a person is**.

> A `Person` detection only means that the model detected an object belonging to the `person` category. It does not perform face recognition or identity identification.

---

## Examples

Detection demonstrations can be stored in:

```text
screenshots/
```

Examples may include:

* Image detection
* Video detection
* Webcam detection

### Example Console Output

```text
Input image : street.jpg

Detected objects:
  person    — 0.94
  car       — 0.88
  bicycle   — 0.81

Objects Detected: 3

Annotated image saved to:
data\output\images\street_detected.jpg
```

---

## Limitations

The current system has the following limitations:

* CPU inference speed is hardware-dependent.
* Real-time FPS is not guaranteed on every computer.
* Detection errors may occur.
* False positives and missed detections are possible.
* Occlusion can reduce detection accuracy.
* Poor lighting can affect detection.
* Motion blur can affect detection.
* Small or distant objects may be difficult to detect.
* Objects outside the 80 COCO classes are not detected.
* Per-frame counting is **not object tracking**.
* The same physical object may be counted repeatedly across different frames.

> **Important:** Detection and tracking are different tasks. This project detects objects independently in each frame and does not assign persistent IDs.

---

## Future Enhancements

The following features are **not implemented** in the current version but could be added in the future:

* Custom dataset training
* Fine-tuning on domain-specific objects
* Object tracking with persistent IDs
* Unique object counting across time
* Image segmentation
* Pose estimation
* GPU and edge-device optimization
* Streamlit interface
* Image/video upload interface
* Confidence threshold slider

---

## Privacy & Responsible Use

* The webcam runs only while the detection window is active.
* Pressing `Q` exits webcam mode.
* The camera is released when processing ends.
* Frames are not intentionally stored unless the snapshot feature is used.
* The project does not perform face recognition.
* The project does not perform identity tracking.
* Detection should not be used for unauthorized surveillance.
* People should be recorded only with appropriate knowledge and consent.

---

## Project Structure

A typical project structure is:

```text
Task_2/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── object_detection.py
│   ├── detector.py
│   └── config.py
│
├── data/
│   ├── input/
│   │   ├── images/
│   │   └── videos/
│   │
│   └── output/
│       ├── images/
│       └── videos/
│
└── screenshots/
```

---

## Conclusion

This project demonstrates a complete **real-time object detection pipeline using a pretrained YOLO model, Python, and OpenCV**.

The system supports:

* Image detection
* Video detection
* Webcam detection
* Bounding-box visualization
* Confidence scores
* Object counting
* FPS display
* Annotated output saving
* Interactive and command-line execution

The project also demonstrates the progression from the classical **Haar Cascade face detector** used in Level 2 to a modern **deep-learning-based YOLO object detector** in Level 3.

A key learning from this project is understanding that **object detection identifies object categories and their locations**, while tasks such as face recognition, identity identification, and object tracking require separate techniques.

---

## Author

**Sandhiya**
AI/ML Intern
**RaushByte Technologies**
