# src/thorlab_loader/metadata.py

from typing import List, Dict
from pathlib import Path
import pandas as pd
import numpy as np
import logging

from .infile_pattern import parse_or_placeholder


class ThorlabMetadata:
    """
    Container for all extracted metadata (XML + filenames).
    Builds a DataFrame with fields:
        filename, channel, stage_x, stage_y, z, t, path
    """

    def __init__(self, xml_meta: Dict, file_paths: List[str]):
        self.xml_meta = xml_meta or {}

        rows = []
        for p in file_paths:
            d = parse_or_placeholder(p)
            d["path"] = p
            d["filename"] = Path(p).name
            rows.append(d)

        df = pd.DataFrame(rows)

        # ---------------------------------------------------------
        # SKIP BAD FILES (e.g., Stack.tif, summary files, etc.)
        # ---------------------------------------------------------
        if "channel" in df.columns:
            bad_rows = df[df["channel"].isna()]
            if not bad_rows.empty:
                skipped = bad_rows["filename"].tolist()
                logging.getLogger(__name__).warning(
                    f"Skipping {len(skipped)} file(s) that do not match expected pattern: {skipped}"
                )
                df = df.drop(index=bad_rows.index).reset_index(drop=True)

        self.df = df



        # Normalize types + log anomalies
        self._coerce_types()

    # ------------------------------------------------------------------
    # TYPE VALIDATION
    # ------------------------------------------------------------------
    def _coerce_types(self):
        """
        Ensures z, t, stage_x, stage_y are integers where possible.
        Warns if float-like values appear unexpectedly.
        """

        int_fields = ["stage_x", "stage_y", "z", "t"]

        for col in int_fields:
            if col not in self.df.columns:
                continue

            # Identify floats
            float_mask = self.df[col].apply(lambda x: isinstance(x, float))
            if float_mask.any():
                bad_vals = self.df.loc[float_mask, col].unique().tolist()
                print(
                    f"[metadata] WARNING: column '{col}' contains float values {bad_vals}. "
                    f"Attempting to cast to integers."
                )

            # Convert to integer where possible
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce").astype("Int64")

    # ------------------------------------------------------------------
    # GROUPING
    # ------------------------------------------------------------------
    def groups(self):
        """
        Yield (group_key, df_group) grouped by:
            (channel, stage_x, stage_y, t)
        Groups include None/NA values (dropna=False).
        Subgroups sorted by z ascending.
        """
        df = self.df.copy()

        grouped = df.groupby(
            ["channel", "stage_x", "stage_y", "t"],
            dropna=False
        )

        for key, sub in grouped:
            if "z" in sub.columns:
                sub = sub.sort_values(by="z", na_position="last")

            yield key, sub

    # ------------------------------------------------------------------
    # INTEGRITY VALIDATION
    # ------------------------------------------------------------------
    def validate_integrity(self):
        """
        Performs consistency checks using XML metadata when available:

        - SizeZ: each (channel, X, Y, T) group must contain exactly SizeZ slices
        - SizeT: global T count must match SizeT
        - Channels: parsed channels must match XML channels (best effort)
        """

        sizez = self.xml_meta.get("SizeZ")
        sizet = self.xml_meta.get("SizeT")
        channels_xml = self.xml_meta.get("Channels")

        # ------------------------------
        # VALIDATE Z-DEPTH
        # ------------------------------
        if sizez is not None:
            bad = []
            for key, sub in self.groups():
                unique_z = sub["z"].dropna().unique().tolist()

                if len(unique_z) == 0:
                    # no z info – skip
                    continue

                if len(unique_z) != sizez:
                    bad.append((key, len(unique_z)))

            if bad:
                raise ValueError(
                    f"XML SizeZ={sizez} mismatch in groups: {bad}"
                )

        # ------------------------------
        # VALIDATE TIME FRAMES
        # ------------------------------
        if sizet is not None:
            tvals = self.df["t"].dropna().unique().tolist()

            if len(tvals) != 0 and len(tvals) != sizet:
                raise ValueError(
                    f"XML SizeT={sizet} but found T values: {sorted(tvals)}"
                )

        # ------------------------------
        # VALIDATE CHANNEL NAMES (best effort)
        # ------------------------------
        if channels_xml:
            ch_xml_norm = [c.lower() for c in channels_xml]
            ch_parsed_norm = [
                str(c).lower()
                for c in self.df["channel"].dropna().unique().tolist()
            ]

            for ch in ch_parsed_norm:
                if not any(ch in cx or cx in ch for cx in ch_xml_norm):
                    raise ValueError(
                        f"Parsed channel '{ch}' not found among XML channels {channels_xml}"
                    )



