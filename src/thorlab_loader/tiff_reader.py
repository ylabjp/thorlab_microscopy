# src/thorlab_loader/tiff_reader.py

import numpy as np
import tifffile


def load_single_tiff(path):
    """
    Load a single TIFF file.
    Returns arr with shape (Z, Y, X) or (Y, X) promoted to (1, Y, X)
    """

    arr = tifffile.imread(path)

    # Ensure array is 3D: (Z, Y, X)
    if arr.ndim == 2:
        arr = arr[None, :, :]   # add Z=1
    elif arr.ndim > 3:
        raise ValueError(f"TIFF has unsupported shape {arr.shape}")

    return arr


def load_tiff_stack(paths):
    """
    Load multiple TIFF files and return array shaped (Z, C, Y, X).
    Assumptions:
      - Each TIFF file corresponds to ONE channel.
      - Each TIFF file may contain Z slices.
    """

    if isinstance(paths, str):
        paths = [paths]

    channel_arrays = []

    for p in paths:
        arr = load_single_tiff(p)    # (Z, Y, X)
        channel_arrays.append(arr)

    # Ensure all channels have same Z, Y, X sizes
    Z = channel_arrays[0].shape[0]
    Y = channel_arrays[0].shape[1]
    X = channel_arrays[0].shape[2]

    for c_idx, arr in enumerate(channel_arrays):
        if arr.shape != (Z, Y, X):
            raise ValueError(
                f"Channel {c_idx} TIFF shape mismatch: {arr.shape} != {(Z, Y, X)}"
            )

    # Stack channels → final shape (Z, C, Y, X)
    full = np.stack(channel_arrays, axis=1)

    return full

