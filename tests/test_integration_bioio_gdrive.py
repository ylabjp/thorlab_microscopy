# tests/test_gdrive_integration.py
import pytest
from pathlib import Path
from thorlab_loader.backends.bioio_thorlab_builder import ThorlabBioioBuilder


@pytest.mark.gdrive_bioio
def test_gdrive_pipeline_bioio(gdrive_dataset, tmp_path):
    dataset_dir = Path(gdrive_dataset)

    xml_path = next(dataset_dir.rglob("Experiment.xml"))
    tiff_dir = xml_path.parent

    out_dir = tmp_path / "gdrive_output"

    builder_bioio = ThorlabBioioBuilder(str(tiff_dir), str(xml_path), out_dir)

    assert out_dir.exists()

