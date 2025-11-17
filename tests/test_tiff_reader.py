import numpy as np
import tifffile
from pathlib import Path
from thorlab_loader.tiff_reader import TiffReader

def test_tiff_reader(tmp_path: Path):
    p = tmp_path / "stack.tif"
    arr = np.zeros((3, 8, 8), dtype=np.uint16)
    tifffile.imwrite(str(p), arr)
    r = TiffReader(p)
    out = r.read()
    assert out.shape == arr.shape

