# Thorlab Microscopy Loader  

**Convert raw Thorlab TIFF files + Experiment.xml into OME-TIFF (Fiji-compatible)**

This package loads Thorlab microscopy outputs — multiple TIFF image planes plus the corresponding `Experiment.xml` metadata — and converts them into a **Fiji/ImageJ-compatible OME-TIFF hyperstack**.

---

## Features

- Automatically load multi-page TIFF stacks from a folder

- Parse Thorlabs Experiment.xml metadata

- Combine Z-slices, channels, and time points into a single OME-TIFF

- Save OME-TIFF compatible with Fiji/ImageJ

- CLI with runtime arguments for input/output paths, verbosity, debug, dry-run, and overwrite

- Colored logging for easy reading

- Automatic detection of missing or misnamed files

---

## Installation

### Clone the repository

```bash
git clone https://github.com/<YOUR_USERNAME/thorlab_microscopy.git
cd thorlab_microscopy
```
### Setup virtual environment using uv

```bash
uv sync
```
### Install package and dependencies in editable mode

```bash
uv pip install -e .
```
--- 

## Usage Example

### Run by the command line

```bash
uv run python run_process_experiment.py --input /path/to/experiment_folder \
                     --xml /path/to/Experiment.xml \
                     --output output.tif \
                     --verbose
```

For more option type 

```bash 
uv run python run_process_experiment.py --help
```
---

## Notes

- Make sure only experiment-related TIFFs are in the input folder.

- Files are sorted alphabetically; sequential numbers (001, 002, …) are required for proper merging.

- If XML metadata exists, ThorlabBuilder can automatically assign channels and Z-slices.

- The CLI supports colored logs and a simple spinner while loading TIFFs.

---

## Contributing

- We welcome contributions! Please follow these rules:

- Fork the repository and create a branch for your feature/fix.

- Make your changes and test locally.

- Avoid committing .pyc or temporary files.

- Open a Pull Request (PR) with a clear description of your changes.

---




