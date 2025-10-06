from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from . import config


def upload_photo(source_path: Path) -> Path:
    """Copy the captured photo into a web-accessible directory."""
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination_dir = config.SHARED_DIR / timestamp
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination = destination_dir / source_path.name
    shutil.copy2(source_path, destination)
    return destination
