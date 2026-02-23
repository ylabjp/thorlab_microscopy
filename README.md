# Thorlab Microscopy Loader  

-*Convert raw Thorlab TIFF files + Experiment.xml into OME-TIFF (Fiji-compatible)**

This package loads Thorlab microscopy outputs — multiple TIFF image planes plus the corresponding `Experiment.xml` metadata — and converts them into a -*Fiji/ImageJ-compatible OME-TIFF hyperstack** for the downstream analysis.

---

## Features

- Automatically load multi-page TIFF stacks from a directory

- Parse Thorlabs Experiment.xml metadata

- Combine Z-slices, channels, and time points into a single OME-TIFF

- Save OME-TIFF compatible with Fiji/ImageJ

- Both options available to run from local disk and from Google Drive 

- Google Drive integration

- Service Account authentication

- OAuth (browser-based user consent)

- Automatic ZIP download & extraction

- CLI with runtime arguments for input/output paths, verbosity, debug, dry-run, and overwrite

- Dataset-level JSON summary metadata

- Colored logging for easy reading

- Automatic detection of missing or misnamed files

---

## Installation

### Clone the repository

```bash
git clone https://github.com/ylabjp/thorlab_microscopy.git
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
## Usage Information
The pipeline supports two exclusive modes:
 
| Mode           | Description                                            |
| -------------- | ------------------------------------------------------ |
| -*Local mode** | Process TIFF + XML already on disk                     |
| -*Drive mode** | Automatically download ZIPs from Google Drive, extract, then process for the test, runs under Pytest|

---

## Local Mode: Existing Data on Disk

```bash
uv run python run_process_experiment.py \
  --tiff_dir /path/to/experiment_folder \
  --xml /path/to/experiment_folder/Experiment.xml \
  --output_dir ./output \
  --verbose
```

### Output behavior: Local mode

- By Default 

```php
<tiff_dir>/output_<dataset_name>/
```
- If --diff\_outdirpath is provided:

```php
<diff_outdirpath>/output_<dataset_name>/
```
---
## Google Drive Mode: ZIP-based datasets for Pytest Only

### Google Drive Authentication: One-Time Setup 

- Before running the program, perform a one-time setup that includes setting up the Google Drive API and supplying the Google Drive URL where all ZIP files are saved.

### Option A: Service Account (Recommended for automation)

- Create a Google Cloud Service Account

- Enable the Google Drive API in your Google Cloud project.

- Configure authentication

- Download service\_account.json

- Ensure the folder permissions are correctly set, share the Drive folder with the service account 
email:

```kotlin
drive-downloader@<project>.iam.gserviceaccount.com
```

Use:
```bash
--auth_mode service_account --service_account path/to/service_account.json
```

### Option B: OAuth (User login via browser)   

- Configure OAuth consent screen (Testing mode is fine)

- Download client\_secret.json

- First run will open a browser for consent

```bash
--auth_mode oauth --client_secret path/to/client_secret.json
```

Credentials and tokens -*Must NOT be Committed**.
Add credentials/ to .gitignore.

---

## Testing: The test suite is organized into three levels.

1. -*Unit tests (default)**

Fast tests using synthetic data.

```bash
uv run pytest tests
```
2. -*Local integration tests (real data)**

Runs the full pipeline on a real local dataset.

````bash
uv run pytest tests \
  -v -m integration \
  --local-tiff-dir /User Tiff Path \
  --local-xml /User XML Path
````
3. -*Google Drive integration tests**

Downloads and processes real datasets from Google Drive using a service account.

```bash
uv run pytest tests \
  -v -m gdrive \
  --gdrive-folder "https://drive.google.com/drive/folders/XXXX" \
  --gdrive-sa-json "/User Path/credentials/service_account.json"
```
-*These tests are opt-in and skipped unless credentials are provided.**
---

### Expected Drive structure
```python
Drive Folder/
 ├── HA\_488\_XYT.zip
 ├── HA\_561\_XYT.zip
 └── ...
```

-*Each ZIP should contain:**
```pgsql
HA_488_XYT/
 ├── ChanA_001_001_001.tif
 ├── ChanB_001_001_001.tif
 └── Experiment.xml
```
---

## Output Directory Logic: Drive Mode

After downloading the zip file/s it will extract each zip file/s in a separate folder for example:

```bash
<work_dir>/extracted/HA_488_XYT/
<work_dir>/extracted/HB_999_XYT/
...
```

For each extracted dataset, it will create output directory like this:

```bash 
<work_dir>/extracted/output_HA_488_XYT/
<work_dir>/extracted/output_HB_999_XYT/ 
...
```

- If --diff\_outdirpath is provided:

```php
<diff_outdirpath>/output_HA_488_XYT/
```

## Summary Files

Each dataset produces:
```pgsql
output_HA_488_XYT/
 ├── dataset_summary.json
 ├── image_001.ome.tif
 └── ...
```
---

## CLI Options (Core)
|Option         |Description                            |
|-------------- |---------------------------------------|
|--tiff\_dir    | Local TIFF directory                  | 
|--xml          | Experiment.xml (local mode)           |
|--drive\_folder|	Google Drive folder URL               |
|--auth\_mode	  | service\_account or oauth             |
|--work\_dir	  | Temp download & extraction directory   |
|--output\_dir	| Base output directory                  |
|--diff\_outdirpath|	Override output base directory     |
|--save\_raw	 |     Also save raw TIFFs                 |
|--verbose	 |       Debug logging                       |

Run:
```bash
uv run python run_process_experiment.py --help
```
---

## JSON Dataset Summary

Each dataset writes a dataset\_summary.json including:

- Dataset name

- Input source (local / drive)

- Number of TIFFs processed

- Channels / Z / Time points

- Output files

- Processing time

- Status (success / failed)

## Notes

- Make sure only experiment-related TIFFs are in the input folder.

- TIFF filenames must follow Thorlabs naming (ChanX_###_###_###.tif)

- ZIP files should contain exactly one dataset

Do not commit credentials
---
---

# Thorlab BioIO Processing Pipeline

-*Reconstruction pipeline for converting Thorlabs microscopy TIFF datasets into validated OME datasets using fully BioIO**.
-*BioIO:** Image Reading, Metadata Conversion, and Image Writing for Microscopy Images in Pure Python.

## This framework:
  - Automatically discovers valid TIFF files  
  - Stacks experimental datasets using BioIO-native logic  
  - Extracts standardized microscopy metadata  
  - Validates physical parameters against Experiment.xml  
  - Writes OME-TIFF (and optionally OME-Zarr) output  
  - Generates detailed JSON validation reports  
  - Provides advanced environment diagnostics and installation if any problem occurs in the run time  

---

## Overview

The pipeline reconstructs experiments from raw Thorlabs acquisitions and diffrent :

Raw TIFF Folder + Experiment.xml
            │
            ▼
Automatic TIFF Selection
(valid acquisition frames only)
            │
            ▼
BioIO Stack Builder
(auto-dimension aware stacking)
            │
            ▼
BioIO Metadata Extraction
(StandardMetadata + physical calibration)
            │
            ▼
XML ↔ Image Cross Validation
(experimental vs reconstructed metadata)
            │
            ▼
Automatic Scientific Output Naming
(Z-stack / Time-series aware)
            │
            ▼
OME Dataset Writer
(OME-TIFF / OME-Zarr)
            │
            ▼
Validation Report + Diagnostics JSON

---

# Architecture

- src/thorlab\_loader/

- backends/
  - bioio\_thorlab\_builder.py # main reconstruction pipeline
  - bioio\_reader.py # BioImage wrapper
  - bioio\_metadata.py # standardized metadata extractor
  - bioio\_writer.py # OME writer

- stacking/
   - bioio\_stack\_builder.py # BioIO-based stacking

- utils/
  - file\_selection.py # TIFF filtering logic
  - outfile\_name.py # scientific output naming

- xml/
  - xml\_parser.py # Experiment.xml parsing

-*Note : These are the main functions and others many do exists and using in the run time** 

---

# Scientific Pipeline

## 1. TIFF Discovery

- Automatically selects only valid experimental TIFF files:

- Example accepted naming: Output\_ChanA\_001\_001\_001.tif

- Non-experimental TIFFs (e.g. Stack.tif) are ignored.

---

## 2. BioIO Stacking 

- Stacking is performed using BioImage-native structures (xarray) rather than manual numpy stacking.

**Supported input dimensions:**

(Z,Y,X)
(C,Z,Y,X)
(T,Z,Y,X)

- Output normalized internally to:  TCZYX

---

## 3. Metadata Extraction

- Extracted via: BioIOMetadataExtractor

**Includes:**

 - dimension order
 - pixel sizes (XYZ)
 - scale factors
 - time interval
 - objective metadata
 - channel information
 - acquisition timestamps

---

## 4. XML Validation

- Experiment.xml is parsed and compared against BioIO metadata.

- **Validation includes:**

 - image size
 - pixel calibration
 - Z depth
 - timepoints
 - channel consistency
 - objective parameters
 - dwell time / frame rate (if available)

---

## 5. Scientific Output Naming

- Output filenames automatically encode experiment structure, with automatically detected Z slice or T series or dual mode:

**Example:**

output\_beada\_001/
Output\_ChanA\_X001\_Y075\_Z001\_stack75\_T001.ome.tif

**Naming reflects:**

- channel
- stage position
- Z stack range
- stack size
- time index

---

## 6. Output Writing

- Primary format: OME-TIFF

- Optional: OME-Zarr

- Compression configurable (default zlib).

---

## 7. Validation Report

A detailed JSON summary is generated:

Output_-.validation.json

**Includes:**

- source input paths
- Time run
- Channel name index(like 0/1..) str(like ChanA..)
- extracted BioIO metadata
- XML comparison results
- validation status
- pipeline version
- Others

---

## 8. Running

uv run python run\_bioio\_process\_experiment.py
--tiff-dir path/to/tiffs
--xml path/to/Experiment.xml
--output-dir output\_root

For more parser argument type: uv run python run\_bioio\_process\_experiment.py --help

---


# If environment issues occur:, don't worry run diagnostic script 

./fix\_env.sh

**Checks:*

- uv environment integrity
- pip availability
- BioIO plugin presence
- Python executable consistency

---

# Common Issues

## Missing plugin

ModuleNotFoundError: bioio\_tifffile

Fix: uv add bioio-tifffile

---

## Broken environment

rm -rf .venv
uv sync

---

# Design Philosophy

This pipeline is designed for:

- reproducible microscopy analysis
- research-grade metadata validation
- large dataset robustness
- plugin-based extensibility

All image operations are delegated to BioIO where possible.

---

## Contributing

- We welcome contributions! Please follow these rules:

- Fork the repository and create a branch for your feature/fix.

- Make your changes and test locally.

- Avoid committing .pyc or temporary files.

- Open a Pull Request (PR) with a clear description of your changes.

---
