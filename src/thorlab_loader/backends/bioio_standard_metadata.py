"""
bioio_standard_metadata.py

Safe standard metadata adapter built on top of bioio.StandardMetadata.
This module MUST NEVER raise if metadata is incomplete.
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from bioio import StandardMetadata


class BioIOStandardMetadata:
    """
    Wrapper around bioio.StandardMetadata with graceful fallback.

    Parameters
    ----------
    bioio_image : BioImage
        Instantiated BioImage object from BioIOReader.
    """

    def __init__(self, bioio_image):
        self._img = bioio_image
        self._metadata: Optional[StandardMetadata] = None
        self._build()

    # ------------------------------------------------------------------
    # Build metadata safely
    # ------------------------------------------------------------------
    def _build(self) -> None:
        """Construct StandardMetadata using best-available information."""
        try:
            dims = getattr(self._img, "dims", None)
            pps = getattr(self._img, "physical_pixel_sizes", None)
        except Exception:
            dims, pps = None, None

        # ---------------------------
        # Dimension sizes
        # ---------------------------
        def _dim_size(axis: str) -> Optional[int]:
            try:
                return getattr(dims, axis)
            except Exception:
                return None

        # ---------------------------
        # Pixel sizes
        # ---------------------------
        def _px(axis: str) -> Optional[float]:
            try:
                return getattr(pps, axis)
            except Exception:
                return None

        # ---------------------------
        # Attempt to read embedded metadata
        # ---------------------------
        try:
            raw_meta = getattr(self._img, "metadata", None)
        except Exception:
            raw_meta = None

        # ---------------------------
        # Build StandardMetadata
        # ---------------------------
        try:
            self._metadata = StandardMetadata(
                dimensions_present=list(dims.order) if dims else None,
                image_size_t=_dim_size("T"),
                image_size_c=_dim_size("C"),
                image_size_z=_dim_size("Z"),
                image_size_y=_dim_size("Y"),
                image_size_x=_dim_size("X"),
                pixel_size_z=_px("Z"),
                pixel_size_y=_px("Y"),
                pixel_size_x=_px("X"),
                objective=self._safe_get(raw_meta, "objective"),
                imaged_by=self._safe_get(raw_meta, "experimenter"),
                imaging_datetime=self._parse_datetime(
                    self._safe_get(raw_meta, "acquisition_date")
                ),
                timelapse=self._infer_timelapse(),
                timelapse_interval=self._infer_time_interval(),
                total_time_duration=None,
                binning=self._safe_get(raw_meta, "binning"),
                row=None,
                column=None,
                position_index=None,
            )
        except Exception as e:
            warnings.warn(f"[BioIO] Failed to construct StandardMetadata: {e}")
            self._metadata = StandardMetadata()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _safe_get(self, obj: Any, key: str) -> Any:
        """Safely fetch attribute or dict key."""
        if obj is None:
            return None

        try:
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)
        except Exception:
            return None

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """Attempt to normalize datetime."""
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt)
                except Exception:
                    continue

        return None

    def _infer_timelapse(self) -> Optional[bool]:
        """Infer timelapse from T dimension."""
        try:
            return self._img.dims.T > 1
        except Exception:
            return None

    def _infer_time_interval(self) -> Optional[timedelta]:
        """
        BioIO rarely exposes time calibration reliably.
        Leave placeholder for future plugin enrichment.
        """
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def standard(self) -> StandardMetadata:
        """Return underlying StandardMetadata object."""
        return self._metadata

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to readable dictionary using BioIO FIELD_LABELS.
        """
        try:
            return self._metadata.to_dict()
        except Exception as e:
            warnings.warn(f"[BioIO] Metadata conversion failed: {e}")
            return {}

    def summary(self) -> str:
        """Pretty printable metadata summary."""
        md = self.to_dict()
        return "\n".join(f"{k}: {v}" for k, v in md.items() if v is not None)

