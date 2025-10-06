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


def _crop_to_slot_aspect(photo: Image.Image, slot_width: int, slot_height: int) -> Image.Image:
    photo_width, photo_height = photo.size
    slot_ratio = slot_width / slot_height
    photo_ratio = photo_width / photo_height

    if abs(photo_ratio - slot_ratio) < 1e-6:
        return photo

    if photo_ratio > slot_ratio:
        # photo is wider -> crop width
        new_width = int(round(photo_height * slot_ratio))
        left = max(0, (photo_width - new_width) // 2)
        crop_box = (left, 0, left + new_width, photo_height)
    else:
        # photo is taller -> crop height
        new_height = int(round(photo_width / slot_ratio))
        top = max(0, (photo_height - new_height) // 2)
        crop_box = (0, top, photo_width, top + new_height)

    return photo.crop(crop_box)


def apply_frame(raw_photo_path: Path, output_path: Optional[Path] = None) -> Path:
    """Overlay the captured photo onto the configured frame artwork."""
    raw_photo_path = Path(raw_photo_path)
    if output_path is None:
        output_path = raw_photo_path
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    frame_path = config.FRAME_IMAGE
    if not frame_path.exists():
        raw_image = Image.open(raw_photo_path).convert("RGB")
        raw_image.save(output_path, quality=95)
        return output_path

    frame_overlay = Image.open(frame_path).convert("RGBA")
    photo_image = Image.open(raw_photo_path).convert("RGBA")
    photo_image = ImageOps.mirror(photo_image)

    slot_width = config.FRAME_SLOT_WIDTH
    slot_height = config.FRAME_SLOT_HEIGHT

    cropped_photo = _crop_to_slot_aspect(photo_image, slot_width, slot_height)
    fitted_photo = cropped_photo.resize((slot_width, slot_height), resample=_get_resample_filter()).convert("RGB")
    filtered_photo = _apply_newspaper_filter(fitted_photo).convert("RGBA")

    canvas = Image.new("RGBA", frame_overlay.size, (0, 0, 0, 0))
    canvas.paste(filtered_photo, (config.FRAME_SLOT_X, config.FRAME_SLOT_Y))
    composite = Image.alpha_composite(canvas, frame_overlay)

    composite.convert("RGB").save(output_path, quality=95)
    return output_path
