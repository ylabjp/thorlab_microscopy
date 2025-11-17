# src/thorlab_loader/xml_parser.py

import xml.etree.ElementTree as ET


def _safe_float(node):
    return float(node.text) if node is not None else None


def parse_experiment_xml(xml_path):
    """
    Parse Thorlabs Experiment.xml.
    Returns dictionary with essential microscope metadata.
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    meta = {}

    # --- Pixel sizes (µm) ---
    px_node = root.find(".//PixelSize/X")
    py_node = root.find(".//PixelSize/Y")
    pz_node = root.find(".//StepSizeZ")

    meta["pixel_size_x"] = _safe_float(px_node)
    meta["pixel_size_y"] = _safe_float(py_node)
    meta["step_size_z"] = _safe_float(pz_node)

    # --- Channel names ---
    meta["channel_names"] = []
    for ch_node in root.findall(".//Channels/Channel"):
        name = ch_node.find("Name")
        if name is not None:
            meta["channel_names"].append(name.text)

    # Provide fallback if no channels detected
    if len(meta["channel_names"]) == 0:
        meta["channel_names"] = None

    return meta

