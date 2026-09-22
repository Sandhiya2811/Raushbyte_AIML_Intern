import os
from pathlib import Path

# Optional .env support — the app works fine without python-dotenv too
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


def _get_str(name: str, default: str) -> str:
    return os.getenv(name, default)


def _get_float(name: str, default: str) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return float(default)     # fall back if .env holds a non-number


def _get_int(name: str, default: str) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return int(default)


# ------------------------------------------------------------------
# Project folders — anchored to this file (no hardcoded personal paths)
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent          # the Task_2 folder

INPUT_IMAGES_DIR = BASE_DIR / "data" / "input" / "images"
INPUT_VIDEOS_DIR = BASE_DIR / "data" / "input" / "videos"
OUTPUT_IMAGES_DIR = BASE_DIR / "data" / "output" / "images"
OUTPUT_VIDEOS_DIR = BASE_DIR / "data" / "output" / "videos"

# ------------------------------------------------------------------
# Model & detection settings
# ------------------------------------------------------------------

# Pretrained YOLO model (auto-downloaded from Ultralytics on first run).
# If your Ultralytics version prefers a different name, use e.g.
# "yolov8n.pt" — the API is identical.
MODEL_PATH = _get_str("MODEL_PATH", "yolo11n.pt")

# Only detections with confidence above this value are shown (0.0 - 1.0)
CONFIDENCE_THRESHOLD = _get_float("CONFIDENCE_THRESHOLD", "0.40")

# Webcam index (0 = default camera)
CAMERA_INDEX = _get_int("CAMERA_INDEX", "0")

# Inference device: "cpu" (default, always works) or a GPU index such as "0"
DEVICE = _get_str("DEVICE", "cpu")

# ------------------------------------------------------------------
# Supported input formats
# ------------------------------------------------------------------

SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv"}