# Project Report — Real-Time Object Detection System using YOLO and Python

**Internship:** AI/ML Internship
**Organization:** RaushByte Technologies
**Task:** Level 3 – Task 2: Computer Vision Project
**Prepared By:** Sandhiya
---

## 1. Introduction

**Computer Vision (CV)** is the AI field that enables computers to interpret images and videos.

A CV system takes raw pixel data and produces meaningful output such as classifications, locations, or descriptions of what is visible.

**Object detection** is one of the core problems in computer vision. It identifies every object of interest in an image and reports both its **category** and **location**.

Object detection powers applications such as:

* Autonomous vehicle perception
* Retail analytics
* Industrial monitoring
* Accessibility systems
* Medical imaging
* Video analytics

---

## 2. Problem Statement

Manually watching footage or inspecting images to find and count objects is slow, error-prone, and difficult to scale.

A system is needed that can automatically:

* Detect multiple object categories simultaneously
* Process images, video files, and live camera streams
* Report each object's location, class, and confidence
* Count objects per frame
* Save annotated results
* Run on ordinary hardware
* Use a pretrained model without collecting or annotating a custom dataset

---

## 3. Objective

The main objectives of this project are:

1. Load a lightweight pretrained YOLO model (`YOLO11-nano`) for inference.
2. Detect objects in **images**, **video files**, and **live webcam streams**.
3. Draw bounding boxes with class names and confidence scores.
4. Count detected objects per frame, including total and per-class counts.
5. Display approximate FPS for video and webcam streams.
6. Allow safe exit using `Q` and save webcam snapshots using the `S` key.
7. Keep the confidence threshold and device configurable.
8. Handle common errors with friendly messages.

---

## 4. Technologies Used

| Technology           | Role                                                                                                                                                      |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Python 3**         | Core programming language                                                                                                                                 |
| **Ultralytics YOLO** | Provides the pretrained YOLO11 model and inference API such as `YOLO(...)` and `model.predict(...)`; handles preprocessing and post-processing internally |
| **PyTorch**          | Deep-learning backend that runs the neural network; installed as an `ultralytics` dependency                                                              |
| **OpenCV**           | Reading images/videos, webcam capture, drawing boxes and labels, displaying frames, and writing annotated outputs                                         |
| **NumPy**            | N-dimensional array mathematics used for image manipulation                                                                                               |
| **argparse**         | Command-line argument parsing                                                                                                                             |
| **pathlib**          | Safe and platform-independent path handling                                                                                                               |
| **datetime / time**  | Timestamps and FPS timing                                                                                                                                 |

---

## 5. Computer Vision Concepts

| Concept               | Meaning                                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Image**             | A grid of pixels; in OpenCV, an image is represented as a NumPy array, commonly using BGR color channels                                                                                         |
| **Frame**             | A single image within a video or camera stream                                                                                                                                                   |
| **Classification**    | Answers: *What is it?* — assigning a category label                                                                                                                                              |
| **Localization**      | Answers: *Where is it?* — producing a bounding box                                                                                                                                               |
| **Object Detection**  | Classification + localization for multiple objects                                                                                                                                               |
| **Bounding Box**      | A rectangle around a detected object, represented here as `(x1, y1, x2, y2)` pixel coordinates                                                                                                   |
| **Confidence Score**  | The model's confidence estimate for a detection; it is a filtering aid, not a guarantee of correctness                                                                                           |
| **Inference**         | Running a trained model on new input to generate predictions                                                                                                                                     |
| **Pretrained Model**  | A model trained previously on a large dataset and reused for inference                                                                                                                           |
| **Transfer Learning** | Reusing knowledge from a pretrained model for a new application, often with further training. This project uses the pretrained model for **inference only**; fine-tuning is a future enhancement |

---

## 6. YOLO Architecture — Conceptual Overview

**YOLO**, meaning **"You Only Look Once"**, was introduced by Joseph Redmon and colleagues in 2015 as a **single-stage object detector**.

Traditional two-stage detectors, such as the R-CNN family, generally separate region proposal and classification stages.

YOLO instead uses a neural network to process the image in a single detection pipeline and predict:

* Bounding boxes
* Object classes
* Confidence scores

This design contributes to YOLO's suitability for fast object detection.

Conceptually, the image can be viewed as being divided into spatial regions, with predictions associated with locations and multiple scales.

Modern Ultralytics YOLO versions use more refined architectures and prediction heads, and exact implementation details vary between versions.

> **Note:** This section provides a conceptual explanation rather than claiming that every YOLO version uses exactly the same internal architecture. For version-specific architecture details, refer to the official Ultralytics documentation.

---

## 7. Pretrained Model

### Selected Model

```text
yolo11n.pt
```

The selected model is the **YOLO11 Nano** variant.

### Model Details

* **Model:** `yolo11n.pt`
* **Variant:** YOLO11 Nano
* **Training Dataset:** COCO
* **Classes:** 80 common object categories
* **Usage:** Inference only
* **Training:** Not performed in this project
* **Fine-tuning:** Not performed in this project

### First Run

During the first run, Ultralytics automatically downloads the pretrained model.

Internet access is therefore required during the initial model download.

After downloading, the model can be reused from the local cache.

### Model Replacement

The model can be replaced with another compatible pretrained model, such as:

```text
yolov8n.pt
```

or a larger YOLO11 variant such as:

```text
yolo11s.pt
```

The exact capabilities and performance depend on the selected model and installed Ultralytics version.

---

## 8. System Architecture

```text
Input
(image / video frame / webcam frame)
        ↓
Preprocessing
(resize + normalization inside model.predict)
        ↓
YOLO Model
(pretrained single-stage detector)
        ↓
Inference
(one forward pass)
        ↓
Post-processing
(confidence threshold + NMS)
        ↓
Bounding Boxes
+ Class Names
+ Confidence Scores
        ↓
Drawing & Counting
(our OpenCV code)
        ↓
Output
(annotated image / video / live window)
```

### Implementation Responsibility

The project separates the responsibilities between the YOLO library and the application's own code.

**YOLO / Ultralytics handles:**

* Model loading
* Input preprocessing
* Neural network inference
* Detection generation
* Confidence filtering
* Post-processing such as NMS

**Our application code handles:**

* Input validation
* Image/video/webcam control
* Drawing bounding boxes
* Displaying labels
* Object counting
* FPS calculation
* Saving output
* User interaction

> **Note:** Preprocessing and post-processing happen inside the YOLO inference pipeline. The application supplies frames to the model and reads the resulting detections.

---

## 9. Image Detection — Implementation

The `detect_image()` function performs the following operations:

1. Validates the input path.
2. Checks the supported image format.
3. Loads the image using `cv2.imread()`.
4. Rejects invalid or corrupted image files.
5. Runs YOLO inference.
6. Extracts detected objects.
7. Draws bounding boxes and labels.
8. Displays confidence scores.
9. Calculates object counts.
10. Prints a per-detection console summary.
11. Saves the annotated image.
12. Displays the result in a preview window.

Example output path:

```text
data/output/images/<name>_detected.jpg
```

Example console output:

```text
Person — 0.94
Car    — 0.88
Dog    — 0.81
```

---

## 10. Video Detection — Implementation

The `detect_video()` function processes a video sequentially.

### Processing Steps

1. Opens the video using `cv2.VideoCapture()`.
2. Reads video metadata such as:

   * FPS
   * Resolution
   * Frame count
3. Creates a `VideoWriter`.
4. Reads one frame at a time.
5. Runs YOLO inference on the current frame.
6. Draws detections and labels.
7. Calculates object counts.
8. Displays the processed frame.
9. Writes the annotated frame to the output video.
10. Continues until the video ends or `Q` is pressed.

The entire video is **not loaded into memory at once**.

Example output:

```text
data/output/videos/<name>_detected.mp4
```

Resources are released using a `finally` block.

---

## 11. Webcam Detection — Implementation

The `detect_webcam()` function provides real-time object detection using the computer's webcam.

### Processing Pipeline

```text
Webcam
   ↓
Capture Frame
   ↓
YOLO Inference
   ↓
Object Detection
   ↓
Draw Bounding Boxes
   ↓
Calculate Counts
   ↓
Calculate FPS
   ↓
Display Frame
   ↓
Capture Next Frame
```

### Controls

| Key | Action                           |
| --- | -------------------------------- |
| `Q` | Exit webcam detection            |
| `S` | Save the current annotated frame |

The webcam is opened using:

```python
cv2.VideoCapture(CAMERA_INDEX)
```

If the camera cannot be opened, the application displays a friendly error message.

The camera is always released using:

```python
cap.release()
cv2.destroyAllWindows()
```

The cleanup is protected using `try/finally`.

---

## 12. Object Counting

The `count_objects(results)` function returns:

```text
(total, {class_name: count})
```

The function iterates over detected class IDs and calculates:

* Total number of detections
* Number of detections for each class

Example:

```text
Total Objects: 5

person: 2
car: 1
dog: 2
```

### Important: Counting vs Tracking

This project performs **per-frame counting**, not object tracking.

For example, if the same person appears in 100 consecutive frames, that person may be counted once in each frame.

Therefore:

> **Per-frame counting does not represent unique objects across time.**

Tracking with persistent IDs is a separate computer vision technique and is planned as a future enhancement.

---

## 13. Confidence Threshold

The default confidence threshold is:

```text
0.40
```

It can be configured using the project's configuration or command-line arguments.

For example:

```powershell
python src/object_detection.py --mode webcam --conf 0.7
```

Detections below the selected confidence threshold are filtered out.

### Effect of Changing the Threshold

**Lower threshold:**

* More detections may appear
* More weak detections may be included
* Noise may increase

**Higher threshold:**

* Fewer detections may appear
* Weak detections are more likely to be removed
* Some valid objects may also be missed

> **Important:** A confidence score is the model's own confidence estimate. It is **not a probability that the detection is correct**, and a high confidence score does not guarantee correctness.

---

## 14. Testing

> **Testing note:** Run each test case yourself and record the actual result. No pass is claimed in advance.

| Test Case          | Input                               | Expected Result                           | Status   |
| ------------------ | ----------------------------------- | ----------------------------------------- | -------- |
| Single object      | Image with one object               | One bounding box with the expected class  | *(fill)* |
| Multiple objects   | Image with several objects          | Multiple boxes and correct counts         | *(fill)* |
| No target objects  | Image without relevant COCO objects | No relevant objects detected              | *(fill)* |
| Low confidence     | Blurred/distant objects             | Weak detections filtered by threshold     | *(fill)* |
| Video              | Sample video                        | Frame-by-frame detection and output video | *(fill)* |
| Webcam             | Live camera                         | Real-time boxes, count, and FPS           | *(fill)* |
| Invalid image      | Nonexistent path                    | Friendly error without crashing           | *(fill)* |
| Invalid video      | Nonexistent path                    | Friendly error without crashing           | *(fill)* |
| Camera unavailable | Disabled/unavailable camera         | Friendly webcam error                     | *(fill)* |
| Quit               | Press `Q`                           | Clean exit and camera release             | *(fill)* |
| Threshold change   | `--conf 0.7`                        | Fewer detections may be shown             | *(fill)* |
| Snapshot           | Press `S` in webcam mode            | Annotated frame saved                     | *(fill)* |

---

## 15. Performance

Actual performance depends on several factors, including:

* YOLO model size
* Input resolution
* CPU vs GPU
* Number of detected objects
* Video resolution
* Computer hardware
* Background processes

Therefore, **no specific FPS is promised**.

### Observed Performance

Fill this section after testing the project on your computer:

```text
Observed webcam FPS: __________ FPS
CPU/GPU: ______________________
Input resolution: ______________
Model: _________________________
```

Example format:

```text
Webcam mode averaged approximately X FPS on CPU.
```

> Replace `X` with the actual value observed during your testing.

### Evaluation Metrics

This project does not perform a quantitative accuracy evaluation, so no accuracy numbers are claimed.

Standard object detection evaluation metrics include:

| Metric        | Meaning                                                                    |
| ------------- | -------------------------------------------------------------------------- |
| **IoU**       | Measures overlap between a predicted bounding box and the ground-truth box |
| **Precision** | Among predicted detections, measures how many are correct                  |
| **Recall**    | Among actual objects, measures how many were detected                      |
| **mAP**       | Mean Average Precision, a standard summary metric for object detection     |

Measuring these metrics would require:

* A labeled evaluation dataset
* Ground-truth bounding boxes
* A defined train/test or validation split
* A fixed evaluation procedure
* Appropriate confidence and IoU thresholds

---

## 16. Limitations

The current system has the following limitations:

* CPU speed is hardware-dependent.
* Real-time FPS is not guaranteed on every computer.
* Detection errors can occur.
* False positives and missed detections are possible.
* Occlusion can reduce detection quality.
* Poor lighting can affect detection.
* Motion blur can reduce detection quality.
* Small or distant objects may be difficult to detect.
* Only the 80 COCO classes are supported.
* Domain-specific objects outside the supported classes are not detected.
* Counting is performed per frame and is not object tracking.
* The model has no concept of a person's identity.
* No face recognition or identity identification is performed.

---

## 17. Privacy and Responsible Use

* Webcam access requires appropriate operating-system permission.
* The detection window remains visible while the camera is active.
* Pressing `Q` exits the webcam detection loop.
* The camera is always released after processing.
* Frames are not stored unless the user explicitly requests a snapshot using `S`.
* The system performs **no face recognition**.
* The system performs **no identity tracking**.
* The system should not be presented as an identity or surveillance system.
* Recording or processing people should be performed only with appropriate knowledge and consent.

---

## 18. Future Enhancements

Possible future improvements include:

1. **Custom Dataset Training**

   * Train or fine-tune YOLO on domain-specific objects.

2. **Object Tracking**

   * Add persistent IDs across frames.

3. **Unique Object Counting**

   * Count each physical object only once across time.

4. **Instance Segmentation**

   * Generate pixel-level object masks.

5. **Pose Estimation**

   * Detect human body keypoints.

6. **GPU Acceleration**

   * Optimize inference for compatible GPUs.

7. **Edge Deployment**

   * Explore formats and runtimes such as ONNX or TensorRT.

8. **Streamlit Interface**

   * Add image/video upload and a confidence-threshold slider.

---

## 19. Conclusion

This project delivered a complete multi-object detection system for:

* Images
* Videos
* Live webcam streams

The system uses a **pretrained YOLO11-nano model** with Python and OpenCV to perform object detection, display bounding boxes, show confidence scores, count objects per frame, monitor FPS, and save annotated outputs.

Compared with the Level 2 Haar Cascade face-detection project, this project represents a progression from a classical, single-purpose detection approach to a modern **deep-learning-based object detector** capable of detecting multiple categories from the COCO dataset.

### Key Learnings

Through this project, I learned:

* The conceptual working of single-stage object detectors
* How pretrained YOLO models perform inference
* The role of confidence thresholds
* The difference between detection, counting, and tracking
* How image, video, and webcam pipelines differ
* How to process video frames sequentially
* How to handle camera and file resources safely
* How to save annotated detection results
* Why confidence scores should not be treated as guaranteed correctness
* The importance of accurately describing a system
* The distinction between pretrained inference and custom model training

> **Project Scope:** This project uses **pretrained YOLO inference only**. No custom training, fine-tuning, face recognition, identity tracking, or quantitative accuracy evaluation is performed.
