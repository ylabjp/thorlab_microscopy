import tempfile
from pathlib import Path
from thorlab_loader.xml_parser import ExperimentXMLParser

def test_xml_parser_basic(tmp_path: Path):
    xml = tmp_path / "Experiment.xml"
    xml.write_text("""
    <Experiment>
      <FramePositions>
        <ZPos>0.0</ZPos>
        <ZPos>1.0</ZPos>
      </FramePositions>
      <Channels>
        <Channel>
          <Name>Ch1</Name>
          <Wavelength>488</Wavelength>
          <Exposure>10</Exposure>
        </Channel>
      </Channels>
      <PixelSizeXY>0.1</PixelSizeXY>
      <ZStepSize>0.5</ZStepSize>
    </Experiment>
    """)
    parser = ExperimentXMLParser(xml)
    md = parser.parse()
    assert md.image_size_x is None or isinstance(md.image_size_x, int)
    assert md.pixel_size_xy_um == 0.1
    assert len(md.channels) == 1
    assert len(md.z_positions_um) == 2

