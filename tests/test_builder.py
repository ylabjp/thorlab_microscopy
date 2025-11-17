import numpy as np
import tifffile
from pathlib import Path
from thorlab_loader.builder import ThorlabImageBuilder

def test_builder_roundtrip(tmp_path: Path):
    # write tiff (Z,Y,X)
    tiff_path = tmp_path / "img.tif"
    arr = np.arange(2*4*4, dtype=np.uint16).reshape(2,4,4)
    tifffile.imwrite(str(tiff_path), arr)

    # write xml
    xml_path = tmp_path / "Experiment.xml"
    xml_path.write_text("""
    <Experiment>
      <FramePositions><ZPos>0</ZPos><ZPos>1</ZPos></FramePositions>
      <Channels><Channel><Name>Ch1</Name></Channel></Channels>
      <PixelSizeXY>0.2</PixelSizeXY>
      <ZStepSize>0.5</ZStepSize>
    </Experiment>
    """)

    builder = ThorlabImageBuilder(tiff_path, xml_path)
    image, meta = builder.load()
    # normalized shape should be (Z, C, Y, X)
    assert image.ndim == 4
    assert image.shape[0] == 2
    assert meta.channels == ["Ch1"]

