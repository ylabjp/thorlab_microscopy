"""
bioio_ultra_stacker.py

Ultra-fast sequential stacker for Thorlab TIFF datasets.

Design goals:
- deterministic ordering
- minimal memory reallocations
- TCZYX-ready output
- safe for large stacks
"""

from pathlib import Path
from typing import List

import numpy as np
import tifffile


# -----------------------------------------------------------
# Internal single read (fast)
# -----------------------------------------------------------
def _read_single(path: str) -> np.ndarray:
    """Read single TIFF as numpy array."""
    return tifffile.imread(path)


# -----------------------------------------------------------
# Nuclear stacker
# -----------------------------------------------------------
def stack_tiffs_ultra(paths: List[str]) -> np.ndarray:
    """
    Stack TIFF files into Z-stack.

    Returns:
        numpy array shaped:
            (Z, Y, X)
    """

    if not paths:
        raise ValueError("No TIFF files provided.")

    # ---- deterministic ordering (VERY IMPORTANT)
    paths = sorted(paths)

    # ---- read first frame to determine shape
    first = _read_single(paths[0])

    if first.ndim != 2:
        raise ValueError(
            f"Expected 2D TIFF frames (Y,X), got shape {first.shape}"
        )

    z = len(paths)
    y, x = first.shape

    # ---- preallocate full array
    stack = np.empty((z, y, x), dtype=first.dtype)

    # insert first
    stack[0] = first

    # ---- sequential fill (fastest reliable)
    for i, p in enumerate(paths[1:], start=1):
        stack[i] = _read_single(p)

    return stack


# -----------------------------------------------------------
# Convert to BioIO canonical TCZYX
# -----------------------------------------------------------
def to_tczyx(stack_zyx: np.ndarray) -> np.ndarray:
    """
    Convert (Z,Y,X) → (T,C,Z,Y,X)

    Default:
        T = 1
        C = 1
    """

    if stack_zyx.ndim != 3:
        raise ValueError("Expected ZYX stack.")

    return stack_zyx[np.newaxis, np.newaxis, :, :, :]

