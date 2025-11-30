# src/thorlab_loader/tiff_writer.py
import tifffile
from pathlib import Path
import numpy as np
from .utils import ensure_parent, log_info

def save_ome_tiff(stack_z_y_x: np.ndarray, out_path: str, axes: str = "TCZYX"):
    """
    stack_z_y_x: (Z, Y, X) -> will be saved as (T=1,C=1,Z,Y,X) with axes 'TCZYX'
    """
    ensure_parent(out_path)
    arr = stack_z_y_x[np.newaxis, np.newaxis, :, :, :]  # (1,1,Z,Y,X)
    # tifffile will build minimal OME-XML if ome=True
    tifffile.imwrite(str(out_path), arr, ome=True, metadata={"axes": "TCZYX"})
    log_info(f"[OK] Saved OME-TIFF → {out_path}")
    return out_path


def save_plain_tiff(stack_z_y_x: np.ndarray, out_path: str):
    """
    Save plain multi-page TIFF where each page is a Z slice.
    """
    ensure_parent(out_path)
    tifffile.imwrite(str(out_path), stack_z_y_x, photometric="minisblack")
    log_info(f"[OK] Saved plain TIFF → {out_path}")
    return out_path
    







#print(f"     Shape={arr5.shape}, axes=TCZYX")

