from pathlib import Path
import os
from typing import List
import xarray as xr
from bioio_tifffile import Reader as TiffReader
#from bioio.readers import Reader as TiffReader
from bioio import BioImage
from typing import List, Tuple
import numpy as np

# ---------------------------------------------------------
# Normalize ANY BioImage to TCZYX xarray
# ---------------------------------------------------------
def normalize_to_tczyx(img: BioImage) -> xr.DataArray:
    """Standardizes any input to a 5D TCZYX xarray without conflicting coords."""

    data = img.xarray_data
    target_dims = ["T", "C", "Z", "Y", "X"]
    
    for d in target_dims:
        if d not in data.dims:
            data = data.expand_dims(d)
    
    data = data.transpose(*target_dims)
    data = data.drop_vars(data.coords.keys())
    return data
# ---------------------------------------------------------
# The Metadata-Aware Universal Stacker
#To make this scientifically complete
#Need to extract the physical coordinates from the xml 
#Attach them to your 5D stack. 
#Ensures that the final file in software like Fiji/ImageJ, 
#"Z-step" or "Time Interval" is already set correctly.
# ---------------------------------------------------------
import os
import xarray as xr
import xml.etree.ElementTree as ET
from pathlib import Path
from bioio import BioImage

def get_thorlabs_params(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Thorlabs specific paths
    z_stage = root.find(".//ZStage")
    lsm = root.find(".//LSM")
    timelapse = root.find(".//Timelapse")
    wavelengths = root.find(".//Wavelengths")
    date_node = root.find(".//Date")   
 
    # Get the target counts
    # Thorlabs calls Z-slices 'steps'
    size_z = int(z_stage.get("steps", 1)) if z_stage is not None else 1

    # Thorlabs calls Time-slices 'timepoints'
    size_t = int(timelapse.get("timepoints", 1)) if timelapse is not None else 1
    
    # Determine Mode
    z_enabled = z_stage.get("enable") == "1" if z_stage is not None else False
    mode = "Z" if (z_enabled and size_z > 1) else "T"
    
    # Get Physical Calibrations: pixelSizeUM is usually in the LSM tag
    pixel_x = float(lsm.get("pixelSizeUM", 1.0)) if lsm is not None else 1.0

    # stepSizeUM is in the ZStage tag
    pixel_z = abs(float(z_stage.get("stepSizeUM", 1.0))) if z_stage is not None else 1.0

    channel_names = [w.get("name") for w in wavelengths.findall("Wavelength")] if wavelengths is not None else ["Force: ChanA"],
    timestamp = date_node.get("date").replace('/', '').replace(' ', '_').replace(':', '') if date_node is not None else "0000"

    return {
        "mode": mode,
        "SizeX": int(lsm.get("width", 512)),
        "SizeY": int(lsm.get("height", 512)),
        "SizeZ": size_z,
        "SizeT": size_t,
        "PixelSizeX": pixel_x,
        "PixelSizeZ": pixel_z,
        "ChannelNames": channel_names,
        "TimesTamp": timestamp, 
        "ZStackEnabled": z_enabled
    }

def get_channel_names_index(xml_dict):
    try:
        # Thorlabs usually nests this under Experiment -> Wavelengths
        wavelengths = xml_dict['ThorImageExperiment']['Wavelengths']['Wavelength']
        
        # If there's only one wavelength, xmltodict might return a dict instead of a list
        if isinstance(wavelengths, dict):
            wavelengths = [wavelengths]
            
        return [w.get('@name', f"Channel {i}") for i, w in enumerate(wavelengths)]
    except (KeyError, TypeError):
        return ["Channel 0"]

def stack_with_bioio_calibrated(tiff_files: list, xml_path: str, min_kb: int = 100):
    params = get_thorlabs_params(xml_path)
    mode = params["mode"]
    target_total = params.get("SizeZ" if mode == "Z" else "SizeT", 0)

    print(f"DEBUG: XML says Target {mode} is {target_total}")

    all_chunks = []
    filtered_files = sorted([f for f in tiff_files if os.path.getsize(f) > 100 * 1024])

    multi_page_list = []
    single_page_list = []

    # Categorize all files first
    for f in filtered_files:
        img = BioImage(f, reader=TiffReader)
        data = normalize_to_tczyx(img)
    
        if data.sizes[mode] > 1:
            multi_page_list.append(data)
            print(f"DEBUG: Identified Multi-page file: {os.path.basename(f)} ({data.sizes[mode]} slices)")
        else:
            single_page_list.append(data)

    # DECISION: Use the big file OR the individual planes (Never both)
    if multi_page_list:
        # Sort by number of slices and take the biggest one
        multi_page_list.sort(key=lambda d: d.sizes[mode], reverse=True)
        best_data = multi_page_list[0]
    
        print(f"DEBUG: Priority Path -> Using 1 multi-page file with {best_data.sizes[mode]} slices.")
        for i in range(best_data.sizes[mode]):
            all_chunks.append(best_data.isel({mode: slice(i, i+1)}))
    else:
        single_page_list.sort(key=lambda x: str(x)) # Simple sort
        
        print(f"DEBUG: Standard Path -> Collecting {len(single_page_list)} individual planes.")
        all_chunks = single_page_list

    print(f"DEBUG: Final unique chunk count: {len(all_chunks)}")

    # Final Stack
    stacked = xr.concat(all_chunks, dim=mode)

    # ATTACH CALIBRATED COORDINATES

    dx = params.get("PixelSizeX", 1.0)
    dy = params.get("PixelSizeY", dx)      # Usually X and Y are the same
    dz = params.get("PixelSizeZ", 1.0)
    dt = params.get("TimelapseInterval", 1.0)

    # This turns index [0, 1, 2...] into physical units [0um, 1.2um, 2.4um...]
    stacked = stacked.assign_coords({
        "X": [i * dx for i in range(stacked.sizes["X"])],
        "Y": [i * dy for i in range(stacked.sizes["Y"])],
        "Z": [i * dz for i in range(stacked.sizes["Z"])],
        "T": [i * dt for i in range(stacked.sizes["T"])]
    })
    # These are used by OME-TIFF writers to set the header correctly
    stacked.attrs["units"] = "micrometers"
    stacked.attrs["time_units"] = "seconds"

    # Add a summary attribute for easy debugging
    stacked.attrs["pixel_size_xyz"] = (dz, dy, dx)

    print(f"[Coordinates] Applied spatial scaling: X/Y={dx}um, Z={dz}um")
    return stacked, filtered_files 

# ---------------------------------------------------------
# Nuclear stacking using BioIO ONLY
# ---------------------------------------------------------
def stack_with_bioio(tiff_files: list, min_kb: int = 100):
    all_planes = []
    valid_files = []
    base_shape = None

    sorted_files = sorted(tiff_files)

    for f in sorted_files:
        if os.path.getsize(f) < min_kb * 1024:
            print(f"[Skip] {Path(f).name} is too small (likely metadata).")
            continue

        try:
            img = BioImage(f, reader=TiffReader)
            data = normalize_to_tczyx(img)

            current_shape = {
                "C": data.sizes["C"],
                "Y": data.sizes["Y"],
                "X": data.sizes["X"]
            }
           
            if base_shape is None:
                base_shape = current_shape
            else:
                # If resolution or channel count changed, we must stop
                if current_shape != base_shape:
                    raise ValueError(
                    f"Mismatched dimensions in {Path(f).name}. "
                    f"Expected {base_shape}, got {current_shape}"
                  ) 
            # ---------------------------------------------
            # Deconstruct Z into individual planes
            # ----------------------------------------------
            if data.sizes["Z"] > 1:
                print(f"[Extract] {Path(f).name} has {data.sizes['Z']} slices. Expanding...")
                for i in range(data.sizes["Z"]):
                    plane = data.isel(Z=slice(i, i+1)) 
                    all_planes.append(plane)
            else:
                all_planes.append(data)
            
            valid_files.append(f)

        except Exception as e:
            print(f"[Error] Skipping  {Path(f).name}: {e}")

    if not all_planes:
        raise RuntimeError("No valid image data found in provided files.")

    #Final Stack
    stacked = xr.concat(all_planes, dim="Z")

    print("--- Stack Complete ---")
    print(f"Final Shape (TCZYX): {stacked.shape}")
    
    return stacked, valid_files





