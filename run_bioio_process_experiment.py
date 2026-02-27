"""
Simple runner for BioIO; Can move with CLI also 

Usage:

uv run python bioio_run_process_experiment.py \
    --tiff-dir ./data \
    --xml ./Experiment.xml \
    --output-dir ./out
    ........................
"""

from pathlib import Path
import argparse

from thorlab_loader.backends.bioio_thorlab_builder import ThorlabBioioBuilder
from thorlab_loader.utils import get_theme, style_print

# =============================================================================
# Argument Parser
# =============================================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="thorlab-bioio",
        description="Convert Thorlabs TIFF + Experiment.xml into validated OME datasets using BioIO",
    )

    parser.add_argument(
        "--tiff-dir",
        required=True,
        type=Path,
        help="Folder containing raw Thorlabs TIFF files",
    )

    parser.add_argument(
        "--xml",
        required=False,
        type=Path,
        help="Experiment.xml path (optional if validation disabled)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default="Output",
        help="Directory to write OME outputs rather than Tiff directory",
    )

    parser.add_argument(
        "--diff_outdirpath",
        type=str,
        default=None,
        help="Optional different base output directory"
    )

    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Disable XML ↔ BioIO metadata validation",
    )

    parser.add_argument(
        "--compression",
        default="zlib",
        help="Compression type (zlib, lzw, etc.)",
    )

    parser.add_argument(
        "--compression-level",
        type=int,
        default=6,
        help="Compression level (0–9)",
    )

    parser.add_argument("--verbose", action="store_true")

    return parser

# =============================================================================
# Main Execution
# =============================================================================

def main() -> None:

    parser = build_parser()
    args = parser.parse_args()
    
    dataset_name = args.tiff_dir.name

    if args.output_dir:
        output_dir = args.output_dir/f"output_{dataset_name}"
    else:
        output_dir = args.tiff_dir.parent/f"output_{dataset_name}"

    output_dir.mkdir(parents=True, exist_ok=True)

    theme = get_theme()

    style_print("\n========== Thorlab BioIO Processing ======================\n", "header")
    style_print(f"Started at: {theme['timestamp']}", "info")
    style_print(f"TIFF directory  : {args.tiff_dir}", "info")
    style_print(f"XML file        : {args.xml}", "info")
    style_print(f"Output directory: {args.output_dir}", "info")
    style_print("\n==========================================================", "header")

    builder = ThorlabBioioBuilder(
        tiff_dir=args.tiff_dir,
        xml_file=args.xml,
        output_dir=output_dir,
        compression=args.compression,
        compression_level=args.compression_level,
        validate_metadata=not args.no_validate,
    )

    builder.build()

    print("=============================================================================")
    style_print("[Builder] DONE. Processing completed successfully : success")
    style_print("Check Summary and validation Report.\n", "info")
    print("================================================================================")

# =============================================================================

if __name__ == "__main__":
    main()

