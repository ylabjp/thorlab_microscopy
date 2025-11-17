import numpy as np
import tifffile
from .metadata import ThorlabMetadata
from .tiff_writer import save_ome_tiff

class ThorlabBuilder:
    def __init__(self, tiff_paths, xml_path):
        self.tiff_paths = list(tiff_paths)
        self.meta = ThorlabMetadata(xml_path)
        self.arr = None

    # Load TIFFs safely
    def load(self):
        stacks = []

        for path in self.tiff_paths:
            img = tifffile.imread(path)

            # Accept 2D or 3D TIFF
            if img.ndim == 2:
                img = img[None]  # → (1, Y, X)

            stacks.append(img)

        # All Z-slices concatenated
        arr = np.concatenate(stacks, axis=0)  # (Z, Y, X)
        self.arr = arr
        print(f"[LOAD] Loaded {len(self.tiff_paths)} files → shape {arr.shape}")
        return arr

    # Save OME-TIFF
    def save(self, output_path, compress=False):
        if self.arr is None:
            self.load()

        save_ome_tiff(output_path, self.arr, self.meta, compress=compress)

