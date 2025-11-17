import numpy as np
import tifffile
from pathlib import Path
from thorlab_loader.metadata import ImageMetadata
from thorlab_loader.tiff_writer import save_ome_tiff

def test_tiff_writer_and_readback(tmp_path: Path):
    out = tmp_path / "out.ome.tif"
    image = np.arange(2*1*6*6, dtype=np.uint16).reshape(2,1,6,6)
    meta = ImageMetadata(axes="ZCYX", pixel_size_xy_um=0.1, pixel_size_z_um=0.5, channels=["Ch1"], dtype=str(image.dtype), shape=image.shape)
    save_ome_tiff(out, image, meta, compress=False)

    # Read back to check shape
    arr = tifffile.imread(str(out))
    # read back may be (Z,1,Y,X) or (Z,Y,X) depending on tifffile handling
    assert arr.ndim in (3,4)

