from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Core configuration values for the photo booth.
COUNTDOWN_SECONDS = 15
OUTPUT_DIR = PROJECT_ROOT / "captures"
CAMERA_INDEX = 0
SECRET_KEY = "local-dev-secret"  # Replace for production deployment

# Asset configuration
ASSETS_DIR = PROJECT_ROOT / "assets"
FRAME_IMAGE = ASSETS_DIR / "breaking_news_frame.png"
# Coordinates (in pixels) describing where the captured photo should appear on the frame.
# Adjust these values to match the artwork precisely.
FRAME_SLOT_X = 610
FRAME_SLOT_Y = 150
FRAME_SLOT_WIDTH = 420
FRAME_SLOT_HEIGHT = 440
