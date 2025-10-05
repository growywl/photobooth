from pathlib import Path
from typing import Optional

from PIL import Image, ImageEnhance, ImageOps

from . import config


def _get_resample_filter() -> int:
    """Return a high-quality resampling filter compatible with Pillow versions."""
    resampling_enum = getattr(Image, "Resampling", None)
    return resampling_enum.LANCZOS if resampling_enum else getattr(Image, "LANCZOS", Image.BICUBIC)


def _apply_newspaper_filter(image: Image.Image) -> Image.Image:
    """Give the photo a vintage newspaper look."""
    grayscale = ImageOps.grayscale(image)
    toned = ImageOps.colorize(grayscale, black="#1b1b1b", white="#f7f1e1")
    contrast = ImageEnhance.Contrast(toned).enhance(1.25)
    brightness = ImageEnhance.Brightness(contrast).enhance(0.95)
    return brightness


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
        raw_image = Image.open(raw_photo_path).convert("RGB")
        raw_image.save(output_path, quality=95)
        return output_path

    frame_image = Image.open(frame_path).convert("RGBA")
    photo_image = Image.open(raw_photo_path).convert("RGBA")
    photo_image = ImageOps.mirror(photo_image)

    slot_width = config.FRAME_SLOT_WIDTH
    slot_height = config.FRAME_SLOT_HEIGHT
    photo_width, photo_height = photo_image.size

    # Scale the captured photo to cover the slot without distorting aspect ratio.
    scale = max(slot_width / photo_width, slot_height / photo_height)
    scaled_size = (
        max(1, int(round(photo_width * scale))),
        max(1, int(round(photo_height * scale))),
    )
    scaled_photo = photo_image.resize(scaled_size, resample=_get_resample_filter())

    # Center-crop the scaled image to the exact slot dimensions.
    excess_width = max(0, scaled_size[0] - slot_width)
    excess_height = max(0, scaled_size[1] - slot_height)
    crop_box = (
        excess_width // 2,
        excess_height // 2,
        excess_width // 2 + slot_width,
        excess_height // 2 + slot_height,
    )
    fitted_photo = scaled_photo.crop(crop_box).convert("RGB")

    filtered_photo = _apply_newspaper_filter(fitted_photo).convert("RGBA")

    # Paste onto the frame using alpha blending.
    frame_image.paste(
        filtered_photo,
        (config.FRAME_SLOT_X, config.FRAME_SLOT_Y),
        mask=filtered_photo,
    )

    frame_image.convert("RGB").save(output_path, quality=95)
    return output_path
