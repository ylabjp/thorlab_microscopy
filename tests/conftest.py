# tests/conftest.py
import pytest
from pathlib import Path


# --------------------------------------------------
# Pytest CLI options
# --------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--gdrive-folder",
        action="store",
        default=None,
        help="Google Drive folder URL for integration tests",
    )
    parser.addoption(
        "--gdrive-sa-json",
        action="store",
        default=None,
        help="Service account JSON path for GDrive tests",
    )
    parser.addoption(
        "--local-tiff-dir",
        action="store",
        default=None,
        help="Local directory containing real TIFF files",
    )
    parser.addoption(
        "--local-xml",
        action="store",
        default=None,
        help="Local Experiment.xml file path",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "unit: fast unit tests (default)",
    )
    config.addinivalue_line(
        "markers",
        "local: tests requiring real local TIFF/XML data",
    )
    config.addinivalue_line(
        "markers",
        "gdrive: tests requiring Google Drive access",
    )
    config.addinivalue_line(
        "markers",
        "integration: integration tests using real local data",
    )


# --------------------------------------------------
# Temporary output directory
# --------------------------------------------------

@pytest.fixture
def tmp_output_root(tmp_path):
    out = tmp_path / "outputs"
    out.mkdir()
    return out


# --------------------------------------------------
# Fake unit-test dataset (CI-safe)
# --------------------------------------------------

@pytest.fixture
def fake_dataset(tmp_path):
    """
    Minimal fake dataset for unit tests
    """
    ds = tmp_path / "dataset"
    ds.mkdir()

    # Fake TIFFs (names must pass initial filters)
    for i in range(3):
        (ds / f"ChanA_{i:03d}.tif").write_bytes(b"FAKE_TIFF")

    # Minimal XML
    (ds / "Experiment.xml").write_text("<Experiment></Experiment>")

    return ds


@pytest.fixture
def fake_local_dataset(fake_dataset):
    """
    (tiff_dir, xml_path) for unit tests
    """
    return fake_dataset, fake_dataset / "Experiment.xml"


# --------------------------------------------------
# Real local dataset (opt-in integration)
# --------------------------------------------------

@pytest.fixture(scope="session")
def local_real_dataset(pytestconfig):
    tiff_dir = pytestconfig.getoption("--local-tiff-dir")
    xml_path = pytestconfig.getoption("--local-xml")

    if not tiff_dir or not xml_path:
        pytest.skip("Local real dataset not provided")

    tiff_dir = Path(tiff_dir)
    xml_path = Path(xml_path)

    if not tiff_dir.exists():
        raise FileNotFoundError(f"TIFF directory not found: {tiff_dir}")
    if not xml_path.exists():
        raise FileNotFoundError(f"XML file not found: {xml_path}")

    return tiff_dir, xml_path


# --------------------------------------------------
# Google Drive dataset (opt-in integration)
# --------------------------------------------------

@pytest.fixture(scope="session")
def gdrive_dataset(pytestconfig, tmp_path_factory):
    folder = pytestconfig.getoption("--gdrive-folder")
    sa_json = pytestconfig.getoption("--gdrive-sa-json")

    if not folder or not sa_json:
        pytest.skip("GDrive credentials not provided")

    from thorlab_loader.download_drive_folder import (
        download_and_extract_drive_folder,
    )

    work_dir = tmp_path_factory.mktemp("gdrive_work")

    extracted = download_and_extract_drive_folder(
        folder_url=folder,
        work_dir=work_dir,
        auth_mode="service_account",
        service_account_json=sa_json,
    )

    return extracted

