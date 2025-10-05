from __future__ import annotations

from pathlib import Path

from PIL import Image

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

# Core configuration values for the photo booth.
COUNTDOWN_SECONDS = 5
OUTPUT_DIR = PROJECT_ROOT / "captures"
CAMERA_INDEX = 0
SECRET_KEY = "local-dev-secret"  # Replace for production deployment

# Asset configuration
ASSETS_DIR = PACKAGE_DIR / "assets"
FRAME_IMAGE = ASSETS_DIR / "breaking_news_frame.png"

# Coordinates (in pixels) describing where the captured photo should appear on the frame.
FRAME_SLOT_X = 560
FRAME_SLOT_Y = 600
FRAME_SLOT_WIDTH = 750
FRAME_SLOT_HEIGHT = 750

# Derived frame metadata
_FALLBACK_WIDTH = 1086
_FALLBACK_HEIGHT = 768
if FRAME_IMAGE.exists():
    with Image.open(FRAME_IMAGE) as frame_asset:
        FRAME_WIDTH, FRAME_HEIGHT = frame_asset.size
else:
    FRAME_WIDTH, FRAME_HEIGHT = _FALLBACK_WIDTH, _FALLBACK_HEIGHT

FRAME_ASPECT_RATIO = FRAME_WIDTH / FRAME_HEIGHT if FRAME_HEIGHT else 1.0
FRAME_SLOT_LEFT_PCT = FRAME_SLOT_X / FRAME_WIDTH if FRAME_WIDTH else 0.0
FRAME_SLOT_TOP_PCT = FRAME_SLOT_Y / FRAME_HEIGHT if FRAME_HEIGHT else 0.0
FRAME_SLOT_WIDTH_PCT = FRAME_SLOT_WIDTH / FRAME_WIDTH if FRAME_WIDTH else 1.0
FRAME_SLOT_HEIGHT_PCT = FRAME_SLOT_HEIGHT / FRAME_HEIGHT if FRAME_HEIGHT else 1.0
