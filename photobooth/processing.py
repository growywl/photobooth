from pathlib import Path
from typing import Optional

from PIL import Image

from . import config


def apply_frame(raw_photo_path: Path, output_path: Optional[Path] = None) -> Path:
    """Overlay the captured photo onto the configured frame artwork."""
    raw_photo_path = Path(raw_photo_path)
    if output_path is None:
        output_path = raw_photo_path
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    frame_path = config.FRAME_IMAGE
    if not frame_path.exists():
        # Frame artwork not available; return the raw capture instead.
        raw_image = Image.open(raw_photo_path)
        raw_image.save(output_path)
        return output_path

    frame_image = Image.open(frame_path).convert("RGBA")
    photo_image = Image.open(raw_photo_path).convert("RGBA")

    # Resize captured photo to fit the target slot on the frame.
    resized_photo = photo_image.resize(
        (config.FRAME_SLOT_WIDTH, config.FRAME_SLOT_HEIGHT),
        resample=Image.Resampling.LANCZOS,
    )

    # Paste onto the frame using alpha blending.
    frame_image.paste(
        resized_photo,
        (config.FRAME_SLOT_X, config.FRAME_SLOT_Y),
        mask=resized_photo,
    )

    frame_image.convert("RGB").save(output_path, quality=95)
    return output_path
