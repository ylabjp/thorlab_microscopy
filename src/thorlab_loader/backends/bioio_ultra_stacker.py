"""
bioio_ultra_stacker.py

Nuclear ultra stacker v2
Auto-detects Thorlab TIFF layout.
"""

from typing import List
import numpy as np
import tifffile


# -----------------------------------------------------------
# Fast reader
# -----------------------------------------------------------
def _read_single(path: str) -> np.ndarray:
    return tifffile.imread(path)


# -----------------------------------------------------------
# Nuclear stacker
# -----------------------------------------------------------

import numpy as np
import tifffile


def _read_tiff_info(path):

    with tifffile.TiffFile(path) as tif:
        pages = len(tif.pages)
        shape = tif.pages[0].shape

    return pages, shape

def stack_tiffs_ultra(paths: List[str]):
    """
    Read list of file paths into numpy stack (Z, Y, X)
    """
    imgs = [read_image(p) for p in paths]
    return np.stack(imgs, axis=0)

'''
def stack_tiffs_ultra(paths):

    if not paths:
        raise ValueError("No TIFF files provided")

    paths = sorted(paths)

    arrays = [tifffile.imread(p) for p in paths]

    shapes = {a.shape for a in arrays}

    if len(shapes) != 1:
        raise RuntimeError(f"Inconsistent TIFF shapes detected: {shapes}")

    shape = arrays[0].shape

    # CASE 1 — each file is Z slice
    if len(shape) == 2:
        return np.stack(arrays, axis=0)   # (Z,Y,X)

    # CASE 2 — each file already contains Z stack
    elif len(shape) == 3:
        print("Each TIFF already contains Z stack — using first file only")

        return arrays[0]   # (Z,Y,X)

    else:
        raise RuntimeError(f"Unsupported TIFF shape {shape}")
'''


'''
def stack_tiffs_ultra(paths):

    paths = sorted(paths)

    arrays = [tifffile.imread(p) for p in paths]
    print(len(paths))

    img = tifffile.TiffFile(paths[0])
    print(len(img.pages))

    shapes = {arr.shape for arr in arrays}

    if len(shapes) != 1:
        raise RuntimeError("Inconsistent TIFF shapes detected.")

    first = arrays[0]

    # Case A — each file is single Z plane
    if first.ndim == 2:
        return np.stack(arrays, axis=0)

    # Case B — each file is full Z stack
    elif first.ndim == 3:

        # Check if all stacks identical
        if all(np.array_equal(first, arr) for arr in arrays[1:]):
            print("[Stacker] All 3D stacks identical. Using first only.")
            return first

        else:
            print("[Stacker] Multiple distinct 3D stacks detected.")
            print("[Stacker] Interpreting files as TIME dimension.")

            return np.stack(arrays, axis=0)  # (T,Z,Y,X)

    else:
        raise ValueError("Unsupported TIFF structure.")
'''

'''
def stack_tiffs_ultra(paths):

    paths = sorted(paths)

    first = tifffile.imread(paths[0])

    # --------------------------------
    # Each file is one Z slice
    # --------------------------------
    if first.ndim == 2:

        z = len(paths)
        y, x = first.shape

        stack = np.empty((z, y, x), dtype=first.dtype)
        stack[0] = first

        for i, p in enumerate(paths[1:], start=1):
            stack[i] = tifffile.imread(p)

        return stack  # (Z,Y,X)

    # --------------------------------
    # Each file already full Z-stack
    # --------------------------------
    elif first.ndim == 3:

        print("[Stacker] TIFF already contains full Z stack.")
        print("[Stacker] Using first file only.")

        return first  # (Z,Y,X)

    else:
        raise ValueError(f"Unsupported TIFF shape: {first.shape}")
'''

'''
def stack_tiffs_ultra(paths: List[str]) -> np.ndarray:
    """
    Supports two layouts:

    CASE 1:
        many 2D TIFFs -> build Z stack

    CASE 2:
        each TIFF already Z stack -> stack as T dimension
    """

    if not paths:
        raise ValueError("No TIFF files provided.")

    paths = sorted(paths)

    first = _read_single(paths[0])

    # --------------------------------------------------
    # CASE 1 — individual Z planes
    # --------------------------------------------------
    if first.ndim == 2:

        z = len(paths)
        y, x = first.shape

        stack = np.empty((z, y, x), dtype=first.dtype)
        stack[0] = first

        for i, p in enumerate(paths[1:], start=1):
            stack[i] = _read_single(p)

        return stack  # (Z,Y,X)

    # --------------------------------------------------
    # CASE 2 — files already contain Z stacks
    # --------------------------------------------------
    elif first.ndim == 3:

        z, y, x = first.shape
        t = len(paths)

        stack = np.empty((t, z, y, x), dtype=first.dtype)
        stack[0] = first

        for i, p in enumerate(paths[1:], start=1):
            stack[i] = _read_single(p)

        return stack  # (T,Z,Y,X)

    else:
        raise ValueError(f"Unsupported TIFF shape: {first.shape}")
'''

# -----------------------------------------------------------
# Convert to BioIO canonical TCZYX
# -----------------------------------------------------------
def to_tczyx(arr: np.ndarray) -> np.ndarray:
    """
    Normalize to TCZYX.

    Supported inputs:
        (Z,Y,X)
        (T,Z,Y,X)
    """

    if arr.ndim == 3:
        # Z,Y,X -> T,C,Z,Y,X
        #return arr[np.newaxis, np.newaxis, :, :, :]
        return arr[np.newaxis, np.newaxis]

    elif arr.ndim == 5:
        # T,Z,Y,X -> T,C,Z,Y,X
        #return arr[:, np.newaxis, :, :, :]
        return arr

    else:
        raise ValueError(f"Unsupported stack shape {arr.shape}")

