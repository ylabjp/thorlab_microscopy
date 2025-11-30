# src/thorlab_loader/xml_parser.py
from pathlib import Path
from lxml import etree
from typing import Dict, List


class ExperimentXMLParser:
    """
    Minimal, robust Experiment.xml parser.
    Raises FileNotFoundError if xml missing.
    extract_metadata returns keys: SizeZ, SizeT, Channels (list), PixelSizeX/Y
    """

    def __init__(self, xml_path: str):
        self.xml_path = Path(xml_path)
        if not self.xml_path.exists():
            raise FileNotFoundError(f"Experiment.xml required but not found: {xml_path}")
        try:
            self.tree = etree.parse(str(self.xml_path))
            self.root = self.tree.getroot()
            self.ns = self.root.nsmap
        except Exception as e:
            raise RuntimeError(f"Failed to parse XML: {e}")

    def _find_pixels(self):
        # try common tags
        pixels = self.root.findall(".//Pixels", namespaces=self.ns)
        return pixels[0] if pixels else None

    def extract_metadata(self) -> Dict:
        pixels = self._find_pixels()
        meta = {"SizeZ": None, "SizeT": None, "Channels": None, "PixelSizeX": None, "PixelSizeY": None}
        if pixels is None:
            return meta
        # SizeZ / SizeT
        try:
            sz = pixels.get("SizeZ")
            meta["SizeZ"] = int(sz) if sz is not None else None
        except Exception:
            meta["SizeZ"] = None
        try:
            st = pixels.get("SizeT")
            meta["SizeT"] = int(st) if st is not None else None
        except Exception:
            meta["SizeT"] = None
        # Channels
        chs = []
        for ch in pixels.findall(".//Channel"):
            name = ch.get("Name") or ch.get("ID") or ch.get("Name")
            if name:
                chs.append(name)
        meta["Channels"] = chs if chs else None
        # pixel sizes
        try:
            px = pixels.get("PhysicalSizeX")
            py = pixels.get("PhysicalSizeY")
            meta["PixelSizeX"] = float(px) if px else None
            meta["PixelSizeY"] = float(py) if py else None
        except Exception:
            meta["PixelSizeX"] = meta["PixelSizeY"] = None
        return meta

