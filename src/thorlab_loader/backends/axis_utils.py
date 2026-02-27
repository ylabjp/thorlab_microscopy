import numpy as np

TARGET_ORDER = "TCZYX"

def normalize_to_tczyx(data: np.ndarray, current_order: str):
    """
    Reorder array to TCZYX standard.
    Missing axes are inserted as size-1.
    """

    # Insert missing dims
    for ax in TARGET_ORDER:
        if ax not in current_order:
            data = np.expand_dims(data, axis=0)
            current_order = ax + current_order

    # Compute permutation
    permute = [current_order.index(ax) for ax in TARGET_ORDER]

    return np.transpose(data, permute)

