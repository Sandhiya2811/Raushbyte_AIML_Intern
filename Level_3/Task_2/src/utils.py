import time
from pathlib import Path

import cv2

from config import (INPUT_IMAGES_DIR, INPUT_VIDEOS_DIR,
                    OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR)

FONT = cv2.FONT_HERSHEY_SIMPLEX

# Distinct BGR colors — each class ID gets a stable color from this palette
PALETTE = [
    (60, 76, 231), (80, 175, 77), (236, 170, 30), (0, 190, 255),
    (200, 60, 220), (180, 120, 40), (50, 200, 200), (140, 140, 255),
    (30, 255, 180), (255, 120, 60), (120, 0, 240), (170, 170, 170),
]


def ensure_directories() -> None:
    """Create the project's data folders if they do not exist yet."""
    for directory in (INPUT_IMAGES_DIR, INPUT_VIDEOS_DIR,
                      OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def class_color(class_id: int):
    """A stable color for a class ID (cycles through the palette)."""
    return PALETTE[int(class_id) % len(PALETTE)]


def _text_with_background(frame, text, position, scale=0.62,
                          color=(0, 255, 0), bg=(0, 0, 0), thickness=2):
    """Draw text on a small filled rectangle so it stays readable."""
    x, y = position
    (text_w, text_h), _ = cv2.getTextSize(text, FONT, scale, thickness)
    cv2.rectangle(frame, (x - 2, y - text_h - 4),
                  (x + text_w + 2, y + 4), bg, -1)
    cv2.putText(frame, text, (x, y), FONT, scale, color, thickness)


def _draw_label(frame, text, x, y, color, scale=0.55, thickness=2):
    """Label on a colored background above the box (inside it if too high)."""
    (w, h), _ = cv2.getTextSize(text, FONT, scale, thickness)
    label_y = y - 6
    if label_y - h - 4 < 0:            # not enough room above the box
        label_y = y + h + 8            # place it just inside instead
    cv2.rectangle(frame, (x, label_y - h - 4),
                  (x + w + 4, label_y + 4), color, -1)
    cv2.putText(frame, text, (x + 2, label_y), FONT, scale,
                (255, 255, 255), thickness)


def draw_detections(frame, results):
    """Draw a bounding box + 'Class Conf' label for EVERY detection.

    Reads xyxy coordinates, class IDs, confidences, and class names
    straight from the Ultralytics Results object.
    """
    for result in results:
        names = result.names
        boxes = result.boxes
        for xyxy, cls_id, conf in zip(boxes.xyxy.tolist(),
                                      boxes.cls.tolist(),
                                      boxes.conf.tolist()):
            x1, y1, x2, y2 = map(int, xyxy)
            color = class_color(cls_id)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{names[int(cls_id)]} {conf:.2f}"
            _draw_label(frame, label, x1, y1, color)
    return frame


def count_objects(results):
    """Return (total_detected, {class_name: count}) for one result set.

    NOTE: this is PER-FRAME counting, not object tracking. The same
    person appearing in 50 video frames is counted 50 times (once per
    frame) — the system does NOT claim they are 50 different people.
    """
    per_class = {}
    for result in results:
        names = result.names
        for cls_id in result.boxes.cls.tolist():
            name = names[int(cls_id)]
            per_class[name] = per_class.get(name, 0) + 1
    return sum(per_class.values()), per_class


def overlay_stats(frame, total, per_class=None, fps=None):
    """Overlay the object count, per-class counts, and optional FPS."""
    lines = [f"Objects Detected: {total}"]
    if per_class:
        for name, count in sorted(per_class.items())[:5]:
            lines.append(f"{name}: {count}")

    y = 30
    for line in lines:
        _text_with_background(frame, line, (10, y), color=(0, 255, 0))
        y += 28

    if fps is not None:
        fps_text = f"FPS: {fps:.1f}"
        (w, _), _ = cv2.getTextSize(fps_text, FONT, 0.62, 2)
        _text_with_background(frame, fps_text,
                              (frame.shape[1] - w - 20, 30),
                              color=(0, 255, 255))
    return frame


class FpsMeter:
    """Smoothed frames-per-second estimator.

    FPS here means approximate RUNTIME PROCESSING SPEED (how many
    frames the pipeline handles per second) — it says nothing about
    model accuracy.
    """

    def __init__(self, smoothing: float = 0.85):
        self._last_time = time.perf_counter()
        self._smoothing = smoothing
        self.fps = None

    def update(self):
        """Call once per processed frame; returns the smoothed FPS value."""
        now = time.perf_counter()
        elapsed = now - self._last_time
        self._last_time = now
        if elapsed > 0:
            instantaneous = 1.0 / elapsed
            if self.fps is None:
                self.fps = instantaneous
            else:
                self.fps = (self._smoothing * self.fps
                            + (1.0 - self._smoothing) * instantaneous)
        return self.fps


def detections_summary(results):
    """Console summary lines like 'Person — 0.94' for every detection."""
    lines = []
    for result in results:
        names = result.names
        for cls_id, conf in zip(result.boxes.cls.tolist(),
                                result.boxes.conf.tolist()):
            lines.append(f"{names[int(cls_id)]} — {conf:.2f}")
    return lines


def save_image(frame, output_path: Path) -> bool:
    """Save an annotated frame; returns True on success."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return bool(cv2.imwrite(str(output_path), frame))