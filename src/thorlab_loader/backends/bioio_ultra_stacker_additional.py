from __future__ import annotations

import numpy as np
import tifffile
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings


# ------------------------------------------------------------
# Fast single TIFF reader
# ------------------------------------------------------------
def _read_single(path: str) -> np.ndarray:
    with tifffile.TiffFile(path) as tif:
        return tif.asarray()


# ------------------------------------------------------------
# Nuclear-level parallel stacker
# ------------------------------------------------------------
def nuclear_stack(
    paths: List[str],
    *,
    expected_dim: str = "Z",  # which axis these files represent
    max_workers: int = 8,
) -> np.ndarray:
    """
    Ultra-fast parallel stacker.

    Parameters
    ----------
    paths : list of TIFF file paths
    expected_dim : which dimension these files represent
        "Z", "T", or "C"
    max_workers : parallel workers

    Returns
    -------
    TCZYX numpy array
    """

    if not paths:
        raise ValueError("No TIFF files provided for stacking.")

    # ------------------------------------------------------------
    # Step 1: Parallel Read
    # ------------------------------------------------------------
    imgs = [None] * len(paths)

    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(_read_single, p): i for i, p in enumerate(paths)}
        for future in as_completed(futures):
            idx = futures[future]
            imgs[idx] = future.result()

    # ------------------------------------------------------------
    # Step 2: Validate shape consistency
    # ------------------------------------------------------------
    shapes = [img.shape for img in imgs]
    if len(set(shapes)) != 1:
        raise ValueError(f"Inconsistent TIFF shapes detected: {set(shapes)}")

    base_shape = imgs[0].shape

    # ------------------------------------------------------------
    # Step 3: Normalize to (Y, X)
    # ------------------------------------------------------------
    if len(base_shape) == 2:
        # YX
        pass
    elif len(base_shape) == 3:
        # Could be ZYX or CYX
        warnings.warn(
            "3D TIFF detected. Assuming (Y,X) per file with stack dimension external."
        )
    else:
        raise ValueError(f"Unsupported TIFF shape: {base_shape}")

    # ------------------------------------------------------------
    # Step 4: Preallocate final array
    # ------------------------------------------------------------
    n = len(imgs)
    Y, X = base_shape[-2], base_shape[-1]

    if expected_dim == "Z":
        data = np.empty((1, 1, n, Y, X), dtype=imgs[0].dtype)
        for i in range(n):
            data[0, 0, i, :, :] = imgs[i]

    elif expected_dim == "T":
        data = np.empty((n, 1, 1, Y, X), dtype=imgs[0].dtype)
        for i in range(n):
            data[i, 0, 0, :, :] = imgs[i]

    elif expected_dim == "C":
        data = np.empty((1, n, 1, Y, X), dtype=imgs[0].dtype)
        for i in range(n):
            data[0, i, 0, :, :] = imgs[i]

    else:
        raise ValueError(f"Unsupported expected_dim: {expected_dim}")

    return data

