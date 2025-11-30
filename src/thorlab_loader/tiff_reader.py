# src/thorlab_loader/tiff_reader.py
from typing import List
import tifffile
import numpy as np


def read_image(path: str) -> np.ndarray:
    """
    Robust read for single image file path.
    Returns a 2D numpy array (Y, X). If image is multi-page, returns first page or raises.
    """
    arr = tifffile.imread(path)
    if arr.ndim == 2:
        return arr
    # common case: (1, Y, X)
    if arr.ndim == 3 and arr.shape[0] == 1:
        return arr.squeeze(0)
    # if arr is multi-page with pages -> stack? but we expect 2D images in each file
    if arr.ndim == 3 and arr.shape[0] > 1:
        # warn and return first page
        return arr[0]
    raise ValueError(f"Unsupported image dimensions: {arr.shape} for file {path}")


def read_stack(paths: List[str]):
    """
    Read list of file paths into numpy stack (Z, Y, X)
    """
    imgs = [read_image(p) for p in paths]
    return np.stack(imgs, axis=0)

