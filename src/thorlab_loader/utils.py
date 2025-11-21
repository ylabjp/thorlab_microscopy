# src/thorlab_loader/utils.py

import os
from pathlib import Path


def ensure_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")


def ensure_list(x):
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

def find_tiff_files(folder: str):
    """
    Find all .tif / .tiff files in a directory and return them sorted.
    """
    folder = Path(folder)
    ensure_exists(folder)
    files = sorted(
        list(folder.glob("*.tif")) + list(folder.glob("*.tiff"))
    )
    return [str(f) for f in files]
