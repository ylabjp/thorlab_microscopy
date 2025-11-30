# src/thorlab_loader/builder.py
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
import math
import pandas as pd
import logging

from .utils import find_tiff_files, log_info, log_warn
from .xml_parser import ExperimentXMLParser
from .metadata import ThorlabMetadata
from .tiff_reader import read_stack
from .tiff_writer import save_ome_tiff, save_plain_tiff

logger = logging.getLogger(__name__)


class ThorlabBuilder:
    """
    Usage:
      b = ThorlabBuilder(tiff_dir, xml_path)
      saved = b.run_and_save(output_dir, save_raw=True)
    """

    def __init__(self, tiff_dir: str, xml_path: str):
        self.tiff_dir = Path(tiff_dir)
        self.xml_path = Path(xml_path)

        if not self.xml_path.exists():
            raise FileNotFoundError("Experiment.xml is required but not found.")

        # Parse XML
        self.xml_meta = ExperimentXMLParser(str(self.xml_path)).extract_metadata()

        # Discover TIFF files
        all_tiffs = find_tiff_files(str(self.tiff_dir))
        if not self.tiff_dir:
            raise FileNotFoundError(f"No TIFF files found in folder {tiff_dir}.")
        log_info(f"Found {len(all_tiffs)} TIFF files in {self.tiff_dir}")
        
       # Skip malformed TIFFs (like Stack.tif)
        self.tiff_files = [
            f for f in all_tiffs
            if ("Chan" in Path(f).name or "CH" in Path(f).name)
        ]

        skipped = len(all_tiffs) - len(self.tiff_files)

        log_info(f"Loaded {len(self.tiff_files)} valid Chan* TIFF files")
        if skipped > 0:
            log_warn(f"Skipped {skipped} non-standard TIFF files")

        if not self.tiff_files:
            raise FileNotFoundError("No valid Chan*.tif files found in folder.")

        # Build metadata table
        self.meta = ThorlabMetadata(self.xml_meta, self.tiff_files)

        # Validate integrity (new function)
        self.meta.validate_integrity()
        log_info("XML integrity check passed (basic)")

    # ----------------------------
    # Metadata grouping
    # ----------------------------

    def build_group_key(self, ch, sx, sy, t):
        return (ch, sx, sy, t)

    def groups(self):
        """Pass-through to metadata.groups()."""
        return list(self.meta.groups())

    # ----------------------------
    # Image stacking
    # ----------------------------

    def build_stack_for_group(self, df_group: pd.DataFrame):
        paths = df_group["path"].tolist()
        stack = read_stack(paths)  # Shape: (Z, Y, X)
        return stack

    # ----------------------------
    # Output name builder
    # ----------------------------

    @staticmethod
    def _validate_and_cast(name: str, value: Union[int, float, str]) -> int:
        # Convert strings → numeric
        if isinstance(value, str):
            try:
                value = float(value) if "." in value else int(value)
            except ValueError:
                raise ValueError(f"[ERROR] Invalid value for {name}: '{value}'")

        # Handle NaN
        if isinstance(value, float) and math.isnan(value):
            raise ValueError(f"[ERROR] Field '{name}' is NaN — filename pattern incomplete.")

        # If numpy integer → convert to Python int
        if isinstance(value, np.integer):
            value = int(value)

        # Float → warn + round
        if isinstance(value, float):
            logger.warning(
                f"[thorlab_loader] Metadata field '{name}' is float ({value}). "
                "Rounding to nearest integer."
            )
            value = int(round(value))

        # Final check
        if not isinstance(value, int):
            raise ValueError(f"[ERROR] Field '{name}' must be int, got: {value}")

        return value
    

    def build_output_name(self, group_key, df_group):
        ch, sx, sy, t = group_key
        sx_i = self._validate_and_cast("StageX", sx)
        sy_i = self._validate_and_cast("StageY", sy)
        t_i = self._validate_and_cast("T", t)

        zvals = (
            df_group["z"]
            .dropna()
            .astype(int)
            .sort_values()
            .unique()
        )

        if len(zvals) == 0:
            zpart = "Zsingle"
        elif len(zvals) == 1:
            zpart = f"Z{zvals[0]:03d}"
        else:
            zpart = f"merged_{zvals.min():03d}To{zvals.max():03d}"

        return f"Output_{ch}_{sx_i:03d}_{sy_i:03d}_{zpart}_{t_i:03d}"

    # ----------------------------
    # Main processing loop
    # ----------------------------

    def run_and_save(self, output_dir: str, save_raw: bool = False) -> List[str]:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        saved = []

        for group_key, df_group in self.groups():
            ch, sx, sy, t = group_key

            if ch is None:
                log_warn(
                    "Skipping unrecognized naming for some files: "
                    f"{df_group['filename'].tolist()[:5]}..."
                )
                continue

            stack = self.build_stack_for_group(df_group)

            base = self.build_output_name(group_key, df_group)

            # OME-TIFF output
            ome_path = out_dir / f"{base}.ome.tif"
            save_ome_tiff(stack, str(ome_path))
            saved.append(str(ome_path))

            # Optional raw TIFF
            if save_raw:
                raw_path = out_dir / f"{base}.tif"
                save_plain_tiff(stack, str(raw_path))
                saved.append(str(raw_path))

        return saved

