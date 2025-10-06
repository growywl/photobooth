from __future__ import annotations

from pathlib import Path

from PIL import Image

try:
    import qrcode  # type: ignore
except ImportError as exc:
    qrcode = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def generate_qr(data: str, output_path: Path) -> Path:
    """Generate a QR code image for the supplied data."""
    if qrcode is None:
        raise RuntimeError(
            "qrcode package is required to generate QR images. Install with `pip install qrcode[pil]`."
        ) from IMPORT_ERROR

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    image.save(output_path)
    return output_path
