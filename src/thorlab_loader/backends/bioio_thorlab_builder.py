from pathlib import Path
from typing import Optional
import json
from datetime import datetime, UTC
from bioio_base.types import PhysicalPixelSizes

# Existing project modules
from ..file_selection import collect_valid_tiffs
#from ..metadata import ThorlabMetadata
from ..xml_parser import ExperimentXMLParser
from ..outfile_name import build_output_name 
from ..utils import hybrid
# BioIO backend
from .bioio_reader import BioIOReader
from .bioio_metadata import BioIOMetadataExtractor
from .bioio_writer import BioIOWriter
from thorlab_loader.utils import style_print

#Stacker
#from .bioio_ultra_stacker import stack_tiffs_ultra, to_tczyx
from .bioio_stack_builder import stack_with_bioio_calibrated, stack_with_bioio, get_thorlabs_params, get_channel_names_index

class ThorlabBioioBuilder:
    """
    Full reconstruction pipeline:

    TIFF discovery → Ultra stacking → BioIOReader →
    Metadata extraction → XML validation → Output naming → Write OME
    """

    def __init__(
        self,
        tiff_dir: Path,
        xml_file: Optional[Path],
        output_dir: Path,
        *,
        compression: str = "zlib",
        compression_level: int = 6,
        validate_metadata: bool = True,
    ):

        self.tiff_dir = Path(tiff_dir)
        self.xml_file = Path(xml_file) if xml_file else None
        self.output_dir = Path(output_dir)

        self.compression = compression
        self.compression_level = compression_level
        self.validate_metadata = validate_metadata

        self.output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # TIFF DISCOVERY + STACK
    # -------------------------------------------------

    def _discover_and_stack(self):

        print("[Builder] Discovering valid TIFF files...")

        tiff_files = collect_valid_tiffs(self.tiff_dir)

        if not tiff_files:
            raise RuntimeError("No valid TIFF files found.")

        print(f"[Builder] Found {len(tiff_files)} usable TIFF files")
        print("[Builder] Ultra stacking images...")

        #stacked_data, tiff_files = stack_with_bioio(tiff_files)

        stacked_data, tiff_files = stack_with_bioio_calibrated(tiff_files, self.xml_file)
        total_depth_um = stacked_data.Z.max().values
        print(f"Total volume depth: {total_depth_um} microns")

        data_to_process = stacked_data.data
        return data_to_process, tiff_files

    # -------------------------------------------------
    # BioIO Processing Reader
    # -------------------------------------------------

    def _load_with_bioio(self, stacked_data):

        print("[Builder] Loading stacked data via BioIOReader...")

        reader = BioIOReader(stacked_data)

        data = reader.read()
        params = get_thorlabs_params(self.xml_file)
        dx = params.get("PixelSizeX", 1.0)
        dy = params.get("PixelSizeY", dx)
        dz = params.get("PixelSizeZ", 1.0)
        channel_names_str = params.get("ChannelNames")
        current_pixel_size = (dz, dy, dx) # The (Z, Y, X) tuple
        channel_names_index = get_channel_names_index(self.xml_file)

        extractor = BioIOMetadataExtractor(
            reader, 
            pixel_size_tuple = current_pixel_size,
            channel_names_index = channel_names_index
        )
        hybrid_channel_name = hybrid(channel_names_index, channel_names_str)
        image_meta = extractor.extract()
        image_meta.dim_order = "TCZYX"

        print(f"Data shape: {data.shape}")
        print(f"Dimension order from reader: {reader.get_dim_order()}")
        print(f"Shape from image meta: {image_meta.shape}")

        return data, image_meta, hybrid_channel_name 

    # -------------------------------------------------
    # XML Validation
    # -------------------------------------------------

    def _validate(self, xml_meta, image_meta):

        print("[Builder] Validating XML <-> BioIO metadata...")

        report = {"status": "PASS", "checks": []}

        def record(name, ok, detail):
            report["checks"].append(
                {"check": name, "ok": ok, "detail": detail}
            )
            if not ok:
                report["status"] = "NOT VALIDATED"

        if xml_meta:

            # spatial size validation
            record("SizeX",
                   xml_meta["SizeX"] == image_meta.shape[-1],
                   f"xml={xml_meta['SizeX']} image={image_meta.shape[-1]}")

            record("SizeY",
                   xml_meta["SizeY"] == image_meta.shape[-2],
                   f"xml={xml_meta['SizeY']} image={image_meta.shape[-2]}")

            # Z depth
            record("SizeZ",
                   xml_meta["SizeZ"] == image_meta.shape[2],
                   f"xml={xml_meta['SizeZ']} image={image_meta.shape[2]}")
        #Pixel calibratio
        if xml_meta["PixelSizeX"] and image_meta.pixel_size:

            diff = abs(xml_meta["PixelSizeX"] - image_meta.pixel_size[2])

            record("PixelSizeX",
                   diff < 1e-3,
                   f"Δ={diff}")
        #Channel count
        record("Channels",
               len(xml_meta["Channels"]) == image_meta.shape[1],
               "channel count")

        print(f"[Builder] Validation status: {report['status']}")
        return report

    def _validate_thorlab_stack(self, xml_meta, image_meta):
        """
        image_meta: The BioImage object (or a custom wrapper) of the stacked data
        xml_meta: Dictionary parsed from Experiment.xml
        """
        report = {"status": "VALIDATED", "checks": []}

        def record(name, ok, msg):
            report["checks"].append({"name": name, "ok": ok, "msg": msg})
            if not ok:
                report["status"] = "NOT VALIDATED"

        if xml_meta:
            #spatial size validation - use size_x, size_y, size_z
            record("SizeX",
               xml_meta["SizeX"] == image_meta.size_x,
               f"xml={xml_meta['SizeX']} image={image_meta.size_x}")

            record("SizeY",
               xml_meta["SizeY"] == image_meta.size_y,
               f"xml={xml_meta['SizeY']} image={image_meta.size_y}")

            #Z depth
            record("SizeZ",
               xml_meta["SizeZ"] == image_meta.size_z,
               f"xml={xml_meta['SizeZ']} image={image_meta.size_z}")

            # Pixel calibration
            if xml_meta.get("pixel_size") and image_meta.pixel_size:
                # index 2 is X in your (Z, Y, X) tuple
                diff = abs(xml_meta["PixelSizeX"] - image_meta.pixel_size[2])
                record("PixelSizeX", diff_x < 1e-4, f"Δ={diff_x:.6f}")

                #Volume/Time Depth Validation
                if xml_meta.get("ZStackEnabled") and xml_meta.get("PixelSizeZ"):
                    diff_z = abs(xml_meta["PixelSizeZ"] - image_meta.pixel_size[0])
                    record("PixelSizeZ", diff_z < 1e-4, f"Δ={diff_z:.6f}")
            else:
                record("SizeT", 
                xml_meta["SizeT"] == image_meta.size_t, 
                f"xml={xml_meta['SizeT']} img={image_meta.size_t}")

            #Channel Count
            xml_chan_count = len(xml_meta.get("Channels", []))
            record("Channels", 
                xml_chan_count == image_meta.size_c, 
                f"xml={xml_chan_count} img={image_meta.size_c}"), 

        style_print("\n========== Validation Results ================", "header")

        for check in report["checks"]:
            status = "PASS" if check["ok"] else "Some Parameters Not validated"
            print(f"[{status}] {check['name']}: {check['msg']}")
        print(f"Final Status: {report['status']}")
        print("=============================================\n")
        return report

    # -------------------------------------------------
    # WRITE OUTPUT
    # -------------------------------------------------

    def _write(self, data, image_meta, output_path):

        print("[Builder] Writing OME output...")

        writer = BioIOWriter(
            output_path,
            compression=self.compression,
            compression_level=self.compression_level,
        )

        writer.write(
            data,
            dim_order=image_meta.dim_order,
            channel_names=None,
            #physical_pixel_sizes=phys_sizes,
            physical_pixel_sizes=image_meta.pixel_size,
        )
    # -------------------------------------------------
    # Validation report
    # -------------------------------------------------

    def _write_report(self, report, image_meta, output_path, hybrid_channel_name):

        report_path = output_path.with_suffix(".validation.json")

        payload = {
            #"timestamp": datetime.datetime.now(datetime.UTC),
            "timestamp": datetime.utcnow().isoformat(),
            "source_tiff_dir": str(self.tiff_dir),
            "Channel_name_hybrid_index_str": hybrid_channel_name, 
            "experiment_xml": str(self.xml_file) if self.xml_file else None,
            "image_metadata": image_meta.to_dict(),
            "validation": report,
            "software": "thorlab_loader + bioio backend",
        }

        with open(report_path, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"[Builder] Validation report → {report_path}")

    # -------------------------------------------------
    # MAIN PIPELINE
    # -------------------------------------------------

    def build(self):
        print("=============================================================================")
        print("[Builder] Starting BioIO reconstruction pipeline")

        stacked_data, tiff_files = self._discover_and_stack()

        data, image_meta, hybrid_channel_name  = self._load_with_bioio(stacked_data)

        xml_meta = None

        if self.validate_metadata and self.xml_file:
            xml = ExperimentXMLParser(self.xml_file)
            xml_meta = xml.extract_metadata()

        report = self._validate_thorlab_stack(xml_meta, image_meta)
        
        Z_stack_val = data.shape[2]
        T_stack_val = data.shape[0]
        output_path = build_output_name(self.output_dir, tiff_files, Z_stack_val, T_stack_val)

        if report["status"] == "VALIDATED":
            self._write(data, image_meta, output_path)

        self._write_report(report, image_meta, output_path, hybrid_channel_name)

        print("[Builder] DONE.")

