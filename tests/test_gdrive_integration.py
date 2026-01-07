# tests/test_gdrive_integration.py
import pytest
from pathlib import Path
from thorlab_loader.builder import ThorlabBuilder


@pytest.mark.integration
@pytest.mark.gdrive
def test_gdrive_pipeline(gdrive_dataset, tmp_path):
    dataset_dir = Path(gdrive_dataset)

    xml_path = next(dataset_dir.rglob("Experiment.xml"))
    tiff_dir = xml_path.parent

    out_dir = tmp_path / "gdrive_output"

    builder = ThorlabBuilder(str(tiff_dir), str(xml_path))
    outputs = builder.run_and_save(str(out_dir))

    assert out_dir.exists()
    assert len(outputs) > 0

