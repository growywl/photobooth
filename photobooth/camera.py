import time
from datetime import datetime
from pathlib import Path

import cv2

from .processing import apply_frame


def run_countdown(seconds: int) -> None:
    """Sleep in one-second increments to keep the server in sync with the UI."""
    for remaining in range(seconds, 0, -1):
        print(f"Capturing photo in {remaining:02d} second(s)...", end="\r", flush=True)
        time.sleep(1)
    print(" " * 40, end="\r")


def capture_photo(camera_index: int, output_dir: Path) -> str:
    """Capture a still frame from the configured camera and save it with the frame."""
    output_dir.mkdir(parents=True, exist_ok=True)

    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Unable to open camera index {camera_index}")

    time.sleep(0.5)  # small delay so auto exposure can settle

    success, frame = camera.read()
    camera.release()

    if not success or frame is None:
        raise RuntimeError("Failed to capture frame from camera")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = output_dir / f"photo_{timestamp}_raw.jpg"
    final_path = output_dir / f"photo_{timestamp}.jpg"

    if not cv2.imwrite(str(raw_path), frame):
        raise RuntimeError(f"Failed to save photo to {raw_path}")

    try:
        saved_path = apply_frame(raw_path, final_path)
    except Exception as error:  # pylint: disable=broad-except
        print(f"Warning: unable to apply frame overlay ({error}). Using raw capture.")
        saved_path = raw_path

    print(f"Photo saved to {saved_path}")
    return Path(saved_path).name
