from thorlab_loader.file_selection import collect_valid_tiffs
from synthetic_tiff import create_fake_stack
from pathlib import Path


def test_collect_valid():

    files = create_fake_stack(3)

    result = collect_valid_tiffs(Path(files[0]).parent)

    assert len(result) == 3
