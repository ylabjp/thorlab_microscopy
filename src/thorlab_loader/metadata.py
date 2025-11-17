import xml.etree.ElementTree as ET

class ThorlabMetadata:
    def __init__(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Extract safe defaults
        self.physical_size_x = self._get_float(root, ".//PixelSize//X", 1.0)
        self.physical_size_y = self._get_float(root, ".//PixelSize//Y", 1.0)
        self.physical_size_z = self._get_float(root, ".//ZStep", 1.0)

        # Channel names (optional)
        self.channel_names = []
        for ch in root.findall(".//Channel"):
            name = ch.get("Name")
            if name:
                self.channel_names.append(name)

    def _get_float(self, root, path, default):
        try:
            elem = root.find(path)
            if elem is not None:
                return float(elem.text)
        except:
            pass
        return default

