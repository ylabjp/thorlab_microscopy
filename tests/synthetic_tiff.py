import numpy as np
import tifffile
import tempfile
from pathlib import Path
import pytest

@pytest.mark.unit
def create_fake_stack(n=5):

    tmp = tempfile.mkdtemp()
    files = []

    for i in range(n):
        arr = np.random.randint(
            0, 65535,
            size=(512,512),
            dtype=np.uint16
        )
        f = Path(tmp)/f"Output_ChanA_001_001_{i:03d}.tif"

        tifffile.imwrite(f, arr)
        files.append(str(f))

    return files
