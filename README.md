# 🧪 Thorlab Microscopy Loader  

**Convert raw Thorlab TIFF files + Experiment.xml into OME-TIFF (Fiji-compatible)**

This package loads Thorlab microscopy outputs — multiple TIFF image planes plus the corresponding `Experiment.xml` metadata — and converts them into a **Fiji/ImageJ-compatible OME-TIFF hyperstack**.

---

## ✅ Features

- Load multi-plane TIFFs (Z-stack, multi-channel, multi-file acquisitions)  
- Parse `Experiment.xml` for physical units and channel info  
- Assemble images + metadata → OME-TIFF  
- Optional compression (LZMA)  
- Fully modular `src` layout  
- Compatible with Python 3.10+  

---

## 📦 Project Structure


---

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/thorlab_microscopy.git
cd thorlab_microscopy

##Create environment + install locally
uv venv
source .venv/bin/activate
uv pip install -e .

Usage Example

Convert a Thorlab acquisition into a Fiji-readable OME-TIFF:

from thorlab_loader.builder import ThorlabBuilder

builder = ThorlabBuilder(
    tiff_paths=[
        "ChanA_001_001_001_001.tif"
    ],
    xml_path="Experiment.xml"
)

builder.save("output.tif", compress=False)


Saved as OME-TIFF

Shape: TCZYX (Time × Channel × Z × Y × X)

Fiji automatically detects channels, slices, and Z-spacing

📄 Required Files
Experiment.xml
ChanA_001_001_001_001.tif
ChanA_001_001_002_001.tif
...

🧠 Workflow

Parse metadata (xml_parser.py) → pixel size, Z-step, channel names

Load TIFFs (tiff_reader.py) → handle 2D or 3D TIFFs, multi-file stacking

Assemble + build (builder.py) → align data with metadata

Write OME-TIFF (tiff_writer.py) → TCZYX layout, Fiji-compatible

🧪 Fiji Compatibility

Opens as a hyperstack

Shows correct channels, slices, timepoints

Pixel size and Z-spacing automatically applied

🔬 Future Extensions

Napari viewer integration

Multi-position acquisitions

Multi-channel datasets

Mosaic stitching / illumination correction

🤝 Contributing

Pull requests welcome

Use ruff and black for formatting


