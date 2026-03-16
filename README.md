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
  --base_path beada_001 \
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

Reconstruction pipeline for converting Thorlabs microscopy TIFF datasets 
through validated OME datasets using BioIO together with the shared
[ylabcommon](https://github.com/ylabjp/ylab-common-scripts) framework.<br>

BioIO provides standardized microscopy image IO and metadata handling, while ylabcommon 
supplies reusable utilities shared across YLab microscopy pipelines (e.g., Thorlab and Keyence).<br>

The Thorlab loader remains responsible for Thorlab-specific dataset handling, while 
shared components such as stacking, metadata utilities, reporting, and writing are provided by ylabcommon.


## This framework:

  - Automatically discovers valid TIFF files  
  - Stacks experimental datasets using BioIO-native logic  
  - Extracts standardized microscopy metadata  
  - Validates physical parameters against Experiment.xml  
  - Writes OME-TIFF (and optionally OME-Zarr) output  
  - Generates detailed JSON validation reports  
  - Provides advanced environment diagnostics and installation if any problem occurs in the run time  

---

## Framework Components

The pipeline reconstructs experiments from raw Thorlabs acquisitions and diffrent :

-> Raw TIFF Folder + Experiment.xmli<br>

-> Automatic TIFF Selection<br>
(valid acquisition frames only)<br>

-> BioIO Stack Builder<br>
(auto-dimension aware stacking)<br>

-> BioIO Metadata Extraction<br>
(StandardMetadata + physical calibration)<br>

-> XML ↔ Image Cross Validation<br>
(experimental vs reconstructed metadata)<br>

-> Automatic Scientific Output Naming<br>
(Z-stack / Time-series aware)<br>

-> OME Dataset Writer<br>
(OME-TIFF / OME-Zarr)<br>

-> Validation Report + Diagnostics JSON<br>

---

# Scientific Pipeline

## TIFF Discovery

- Automatically selects only valid experimental TIFF files:

- Example accepted naming: Output\_ChanA\_001\_001\_001.tif

- Non-experimental TIFFs (e.g. Stack.tif) are ignored.

---

## BioIO Stacking 

- Stacking is performed using BioImage-native structures (xarray) rather than manual numpy stacking.

**Supported input dimensions:**

(Z,Y,X)<br>
(C,Z,Y,X)<br>
(T,Z,Y,X)<br>

- Output normalized internally to:  TCZYX

---

## Metadata Extraction

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

## XML Validation

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

## I/O dataset structure

### Example Input Dataset

- Thorlab acquisitions contain TIFF planes structured by channel: 
    - X stage position
    - Y stage position
    - Z slice and time index.

### Example:

```PostgreSQL
dataset/
├── ChanA_001_001_001_001.tif
├── ChanA_001_001_002_001.tif
├── ChanA_001_001_003_001.tif
├── ChanB_001_001_001_001.tif
└── ...
```

### Filename structure:

| Item | Description |
|:-----|:------------|
|ChanA |Channel name |
|001  |X stage position|
|001  |Y stage position |
|0016 |Z slice|
|001  |Time index|

## Example Output Dataset

Output datasets are written into a timestamped directory, preserving the experiment input structure.

             Format:(YYMMDD9)(Time)
Thorlab_Output_20260311_081658/
  &ensp;beada_001/
    &ensp;&ensp;ChanA_X001_Y001_Z001_to_Z075_stack_T001.ome.tif
    &ensp;&ensp;ChanA_X001_Y001_Z001_to_Z075_stack_T001.validation.json
    &ensp;&ensp;ChanA_X001_Y001_Z001_to_Z075_stack_T001.report.txt

**Where:**

- Thorlab_Output_YYYYMMDD_HHMMSS is automatically generated

- the dataset folder corresponds to the input experiment directory

- stack outputs and reports are saved together

---

## Scientific Output Name 

Output filenames automatically encode the experiment structure.

- Example:  ChanA_X001_Y001_Z001_to_Z075_stack_T001.ome.tif

- Information Encoded in Output Filename

|Item	| Description|
|:-----|:------------|
|ChanA	|Channel name|
|X001	|X stage position|
|Y001	|Y stage position|
|Z001_to_Z075	|Z stack range|
|stack |Stacked dataset|
|T001	|Timepoint|

---

## Multi-Position Experiments

If multiple stage positions are present (e.g. XY scanning), the pipeline will generate stacks for each position.

Example input:<br>

ChanA_001_001_001_001.tif
ChanA_002_001_001_001.tif
ChanA_003_001_001_001.tif

Possible output:<br>

ChanA_X001_Y001_Z001_to_Z075_stack_T001.ome.tif
ChanA_X002_Y001_Z001_to_Z075_stack_T001.ome.tif
ChanA_X003_Y001_Z001_to_Z075_stack_T001.ome.tif

---

## Dataset Report

Each processed dataset generates two report files.<br>
                                                              == **Summary Report** ==<br>
ChanA_X001_Y001_Z001_to_Z075_stack_T001.validation.json       ->  *Good for machine readeable* 
ChanA_X001_Y001_Z001_to_Z075_stack_T001.report.txt            ->  *Easy for human quick look*

---

### Purpose:

- File	Description  
  -- .validation.json	Machine-readable validation report
  -- .report.txt	Human-readable summary report

- These reports include:

   - detected dataset dimensions

   - extracted BioIO metadata

   - XML comparison results

   - validation status

  - environment diagnostics

---

## Summary

The Thorlab pipeline reconstructs datasets by:

discovering valid TIFF planes

stacking Z slices, channels, and timepoints

validating metadata against Experiment.xml

generating scientific output filenames

writing Fiji-compatible OME-TIFF datasets

producing validation reports


---

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

## How to Run

### For the test run with data 

```bash

uv run python run_bioio_process_experiment.py \
--tiff-dir < Like: InFileThorlab/beada_001 > \
--xml < Like: /InFileThorlab/beada_001/Experiment.xml> \
--base_path <Like: beada_001> \
--output-dir <Like: dirX > 
--diff_outdirpath < Build Output path > 
--singlefilerun

```

For more parser argument type: uv run python run\_bioio\_process\_experiment.py --help

**Note :** We can make it CLI run to run it easily 

### Run with input zip files, big chunk data

- The pipeline processes all datasets automatically
- Output directories follow the structure of the input ZIP file paths
- Generated files are saved with timestamped names to avoid overwriting previous results

```bash

uv run python run_bioio_process_experiment.py \
--output-dir < dirX > \
--diff_outdirpath < Build Output path > \
--infile_yaml <Data file example : dataset_thorlab.yaml>

```
---

## Run Unit Tests

 -**Unit tests (default)**

```bash
uv run pytest -m unit
```
-**Local dataset validation**

```bash
uv run pytest tests/ -m integration\_bioio 
  --local-tiff-dir "Your local tiff's directory path" 
  --local-xml \
```
-**Google Drive dataset**

```bash

uv run pytest tests \
  -v -m gdrive_bioio -s --gdrive-folder \
  --gdrive-folder "URL" \
  --gdrive-sa-json "/credentials.json"
```
---

# If environment issues occur:, don't worry run diagnostic script 

```bash

source env_common_fix.sh

```
---

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

---

```bash
rm -rf .venv
uv sync
```
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
