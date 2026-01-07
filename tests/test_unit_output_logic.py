import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from thorlab_loader.builder import ThorlabBuilder


@pytest.mark.unit
def test_output_created_unit(fake_local_dataset, tmp_output_root, monkeypatch):
    tiff_dir, xml_path = fake_local_dataset

    import thorlab_loader.builder as builder_module

    # --------------------------------------------------
    # 1. Mock ThorlabMetadata
    # --------------------------------------------------
    class FakeMetadata:
        def __init__(self, xml_meta, tiff_files):
            pass

        def validate_integrity(self):
            return True

        def groups(self):
            df = pd.DataFrame(
                {
                    "path": [str(tiff_dir / "ChanA_000.tif")],
                    "filename": ["ChanA_000.tif"],
                    "z": [0],
                }
            )
            group_key = ("A", 0, 0, 0)
            return [(group_key, df)]

    monkeypatch.setattr(
        builder_module,
        "ThorlabMetadata",
        FakeMetadata,
    )

    # --------------------------------------------------
    # 2. Mock read_stack (no real TIFF IO)
    # --------------------------------------------------
    monkeypatch.setattr(
        builder_module,
        "read_stack",
        lambda paths: np.zeros((1, 10, 10)),
    )

    # --------------------------------------------------
    # 3. Mock save_ome_tiff (no real file write)
    # --------------------------------------------------
    monkeypatch.setattr(
        builder_module,
        "save_ome_tiff",
        lambda stack, path: Path(path).touch(),
    )

    # --------------------------------------------------
    # Run
    # --------------------------------------------------
    out_dir = tmp_output_root / "unit_case"

    builder = ThorlabBuilder(str(tiff_dir), str(xml_path))
    outputs = builder.run_and_save(str(out_dir))

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------
    assert out_dir.exists()
    assert len(outputs) == 1
    assert outputs[0].endswith(".ome.tif")

