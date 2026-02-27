from __future__ import annotations
from pathlib import Path
import numpy as np
from bioio import BioImage, DimensionNames
from .bioio_metadata import BioIOMetadataExtractor
import warnings
#from bioio import DimensionNames

class BioIOReader:
    '''
    Wrapper around BioImage.

    Responsibilities:
    - Open file with BioIO
    - Normalize output to TCZYX numpy array
    - Expose dimensions (NO metadata interpretation here)
    '''

    def __init__(self, image_data):
        #self.image_path = Path(image_data)
        self._img = BioImage(self.image_data)

    # ---------------------------
    # Rturns TCZYX numpy array
    # ---------------------------
    def get_data(self):
        try:
            return self._img.data
        except Exception as e:
            warnings.warn(f"[BioIO] Unable to read pixel data: {e}")
            return None

    # ---------------------------
    # Rturns TCZYX xarray data array
    # ---------------------------
    def get_xarray(self):
        try:
            return self._img.xarray_data
        except Exception as e:
            warnings.warn(f"[BioIO] xarray view unavailable: {e}")
            return None

    # ---------------------------
    # Dimensions
    # ---------------------------
    def get_dims(self):
        try:
            return self._img.dims
        except Exception as e:
            warnings.warn(f"[BioIO] dims unavailable: {e}")
            return None

    # ---------------------------
    # Returns string TCZYX
    # ---------------------------
    def get_dim_order(self):
        try:
            return self._img.dims.order
        except Exception as e:
            warnings.warn(f"[BioIO] dim order unavailable: {e}")
            return None

    # ---------------------------
    # Dimensions X
    # ---------------------------
    def get_dim_order(self):
        try:
            return self._img.dims.X
        except Exception as e:
            warnings.warn(f"[BioIO] dim X order unavailable: {e}")
            return None

    # ---------------------------
    # Returns tuple of dimension
    # ---------------------------
    def get_shape(self):
        try:
            return self._img.shape
        except Exception as e:
            warnings.warn(f"[BioIO] shape unavailable: {e}")
            return None

    def get_size(self, axis: str):
        """
        Example: get_size("X"), get_size("C")
        """
        try:
            return getattr(self._img.dims, axis)
        except Exception:
            warnings.warn(f"[BioIO] axis '{axis}' not present")
            return None

    # ---------------------------
    # Scene handling
    # ---------------------------
    def get_scenes(self):
        try:
            return self._img.scenes
        except Exception:
            warnings.warn("[BioIO] scenes not available")
            return []

    def set_scene(self, scene):
        try:
            self._img.set_scene(scene)
        except Exception as e:
            warnings.warn(f"[BioIO] cannot set scene {scene}: {e}")

    # ---------------------------
    # Metadata
    # ---------------------------
    def get_standard_metadata(self):
        try:
            return self._img.standard_metadata
        except Exception:
            warnings.warn("[BioIO] standard metadata unavailable")
            return None

    # ---------------------------
    #Return BioIO PhysicalPixelSizes object (Z, Y, X).
    # ---------------------------
    def get_physical_pixel_sizes(self):
        try:
            return self._img.physical_pixel_sizes
        except Exception as e:
            warnings.warn("[BioIO] pixel size metadata unavailable: {e}")
            return None

    # ---------------------------
    #Return pixel sizes as a simple dict:
    # ---------------------------
    def get_physical_pixel_sizes_dict(self):
        try:
            p = self._img.physical_pixel_sizes
            if p is None:
                return {"Z": None, "Y": None, "X": None}

            return {"Z": p.Z, "Y": p.Y, "X": p.X}

        except Exception as e:
            warnings.warn(f"[BioIO] Unable to normalize pixel sizes: {e}")
            return {"Z": None, "Y": None, "X": None}

    # ---------------------------
    # Flexible slicing
    # ---------------------------
    def get_image_data(self, order="CZYX", **kwargs):
        """
        Example:
        get_image_data("CZYX", T=0)
        """
        try:
            return self._img.get_image_data(order, **kwargs)
        except Exception as e:
            warnings.warn(f"[BioIO] get_image_data unavailable: {e}")
            return None

    # ---------------------------
    #Returns axis summary using ONLY safe accessors.
    # ---------------------------
    def get_summarize_dimensions(self):
        summary = {}

        dims = self.get_dims()
        shape = self.get_shape()

        if dims is None or shape is None:
           return summary

        for axis in dims.order:
            size = self.get_size(axis)
            props = self.get_axis_properties(axis)

            summary[axis] = {
                "size": size,
                "properties": str(props) if props else None,
            }
        return summary


    _DIMENSION_MAP = {
      DimensionNames.Time: "T",
      DimensionNames.Channel: "C",
      DimensionNames.SpatialZ: "Z",
      DimensionNames.SpatialY: "Y",
      DimensionNames.SpatialX: "X",
    }

    def get_normalized_dimension_order(self):
        """
        Always return TCZYX-style order regardless of plugin naming.
        """
        dims = self.get_dims()
        if dims is None:
            return None

        order = []

        for axis in dims.order:
            mapped = _DIMENSION_MAP.get(axis, axis)
            order.append(mapped)

        return "".join(order)

    # ---------------------------
    #Return BioIO Scale object (T, C, Z, Y, X).
    #seconds between timepoints:T, spatial calibration matches pixel size
    # ---------------------------
    def get_scale(self):
        try:
            return self._img.scale
        except Exception as e:
            warnings.warn(f"[BioIO] Scale unavailable: {e}")
            return None

    # ---------------------------
    #Return scale as a simple dict:
    # ---------------------------
    def get_scale_dict(self):
        try:
            s = self._img.scale
            if s is None:
                return {"T": None, "C": None, "Z": None, "Y": None, "X": None}

            return {
              "T": s.T,
              "C": s.C,
              "Z": s.Z,
              "Y": s.Y,
              "X": s.X,
            }

        except Exception as e:
            warnings.warn(f"[BioIO] Unable to normalize scale: {e}")
            return {"T": None, "C": None, "Z": None, "Y": None, "X": None}

    # ---------------------------
    #Unified access to physical calibration (T, Z, Y, X spacing).
    # ---------------------------
    def get_physical_units(self):
        result = {ax: {"spacing": None, "unit": None} for ax in ["T", "C", "Z", "Y", "X"]}

    #PhysicalPixelSizes (preferred for XYZ)
        try:
            pps = getattr(self._img, "physical_pixel_sizes", None)

            if pps:
                if pps.Z is not None:
                    result["Z"] = {"spacing": float(pps.Z), "unit": "µm"}
                if pps.Y is not None:
                    result["Y"] = {"spacing": float(pps.Y), "unit": "µm"}
                if pps.X is not None:
                    result["X"] = {"spacing": float(pps.X), "unit": "µm"}

        except Exception as e:
            warnings.warn(f"[BioIO] PhysicalPixelSizes unavailable: {e}")

    #Scale fallback (some formats only expose this)
        try:
            scale = getattr(self._img, "scale", None)

            if scale:
                for ax in ["Z", "Y", "X"]:
                    if result[ax]["spacing"] is None:
                        val = getattr(scale, ax, None)
                        if val is not None:
                            result[ax] = {"spacing": float(val), "unit": "µm"}

        except Exception as e:
           warnings.warn(f"[BioIO] Scale unavailable: {e}")

    #TimeInterval → timedelta → seconds
        try:
            ti = getattr(self._img, "time_interval", None)

            if ti is not None:
                result["T"] = {
                  "spacing": float(ti.total_seconds()),
                  "unit": "s"
               }

        except Exception as e:
           warnings.warn(f"[BioIO] TimeInterval unavailable: {e}")

        return result

    # ---------------------------
    #Return normalized channel metadata independent of file format.
    # ---------------------------
    def get_channel_info(self):

        channels = []

    # Determine number of channels safely
        try:
            dims = self._img.dims
            size_c = dims.C if hasattr(dims, "C") else 1
        except Exception:
            warnings.warn("[BioIO] Cannot determine channel dimension; assuming 1.")
            size_c = 1

    # Try BioIO channel metadata (OME-style)
        try:
            ch_meta = getattr(self._img, "channel_names", None)

            if ch_meta:
                for i, name in enumerate(ch_meta):
                    channels.append({
                      "index": i,
                      "name": str(name) if name else f"C{i}",
                      "emission_nm": None,
                   })

        except Exception as e:
            warnings.warn(f"[BioIO] channel_names unavailable: {e}")

    # Try OME rich metadata (if available)
        if not channels:
            try:
                ome = getattr(self._img, "ome_metadata", None)

                if ome and hasattr(ome, "channels"):
                    for i, ch in enumerate(ome.channels):
                        emission = getattr(ch, "emission_wavelength", None)

                        channels.append({
                          "index": i,
                          "name": ch.name or f"C{i}",
                          "emission_nm": float(emission) if emission else None,
                       })

            except Exception as e:
                warnings.warn(f"[BioIO] OME channel metadata unavailable: {e}")

    # Absolute fallback (guaranteed return)
        if not channels:
            for i in range(size_c):
                channels.append({
                  "index": i,
                  "name": f"C{i}",
                  "emission_nm": None,
               })

        return channels

    # From metadata.Py, all featured added in this file
    def get_metadata_all(self):
        if not hasattr(self, "_metadata_obj"):
            self._metadata_obj = BioIOMetadataExtractor(self._img)
        return self._metadata_obj
