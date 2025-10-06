from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def print_photo(image_path: Path) -> bool:
    """Attempt to send the captured photo to the default system printer."""
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        system = platform.system().lower()
        if "windows" in system:
            # os.startfile is Windows-only; fall back to rundll32 if unavailable.
            try:
                os.startfile(str(image_path), "print")  # type: ignore[attr-defined]
                return True
            except AttributeError:
                subprocess.run(
                    [
                        "rundll32",
                        "%s" % Path("C:/windows/system32/shimgvw.dll"),
                        "ImageView_PrintTo",
                        str(image_path),
                    ],
                    check=False,
                )
                return True
        elif "darwin" in system:
            subprocess.run(["lp", str(image_path)], check=False)
            return True
        else:
            subprocess.run(["lp", str(image_path)], check=False)
            return True
    except Exception as error:  # pylint: disable=broad-except
        print(f"Print warning: {error}")
        return False
