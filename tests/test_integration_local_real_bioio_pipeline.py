import pytest
from thorlab_loader.backends.bioio_thorlab_builder import ThorlabBioioBuilder


@pytest.mark.integration_bioio
def test_full_pipeline_bioio(local_real_dataset):
    tiff_dir, xml_file = local_real_dataset
    if not tiff_dir:
        pytest.skip("No local dataset provided")

    builder = ThorlabBioioBuilder(
        tiff_dir = str(tiff_dir),
        xml_file = str(xml_file),
        output_dir = "Ptest_output"
    )

    builder.build()

    assert True

