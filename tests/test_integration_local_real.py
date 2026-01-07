import pytest
from thorlab_loader.builder import ThorlabBuilder


@pytest.mark.integration
def test_real_local_pipeline(local_real_dataset, tmp_path):
    tiff_dir, xml_path = local_real_dataset

    out_dir = tmp_path / "outputs"

    builder = ThorlabBuilder(
        tiff_dir=str(tiff_dir),
        xml_path=str(xml_path),
    )

    outputs = builder.run_and_save(str(out_dir))

    assert out_dir.exists()
    assert len(outputs) > 0

    for f in outputs:
        assert f.endswith(".ome.tif")

