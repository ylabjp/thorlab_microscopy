#!/usr/bin/env python3
import argparse
import logging
import sys
import threading
import time
from pathlib import Path

from thorlab_loader.builder import ThorlabBuilder
from thorlab_loader.utils import find_tiff_files
from thorlab_loader.tiff_writer import save_ome_tiff


# -----------------------------
# Colored Logging Helpers
# -----------------------------
def setup_logging(args):
    level = logging.WARNING
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(message)s"
    )


def log_info(msg):
    logging.info(f"\033[94m[INFO]\033[0m {msg}")


def log_done(msg):
    logging.info(f"\033[92m[DONE]\033[0m {msg}")


def log_warn(msg):
    logging.warning(f"\033[93m[WARN]\033[0m {msg}")


def log_error(msg):
    logging.error(f"\033[91m[ERROR]\033[0m {msg}")


# -----------------------------
# Spinner for running indication
# -----------------------------
class Spinner:
    def __init__(self, message="Running"):
        self.message = message
        self.spinner = ['|', '/', '-', '\\']
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def _spin(self):
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{self.message}... {self.spinner[idx % len(self.spinner)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
        sys.stdout.write("\r" + " " * (len(self.message) + 5) + "\r")  # clear line

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


# -----------------------------
# Argument Parser
# -----------------------------
def parse_args():
    import textwrap

    parser = argparse.ArgumentParser(
        prog="Thorlabs Microscopy Converter",
        description=(
            "Convert Thorlabs microscopy TIFF stacks + Experiment.xml "
            "into a clean OME-TIFF file."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              Convert all TIFFs in folder:
                python run.py -i InFile/bead_001 -o out/output.ome.tif

              Debug mode:
                python run.py -i raw/ -o out/out.ome.tif --debug

              Dry-run (no output file):
                python run.py -i raw/ --dry-run
            """
        ),
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input TIFF file OR folder containing TIFF files."
    )

    parser.add_argument(
        "-o", "--output",
        required=False,
        default="output.ome.tif",
        help="Output OME-TIFF filename (default: output.ome.tif)"
    )

    parser.add_argument(
        "-x", "--xml",
        required=False,
        help="Path to Experiment.xml (optional if inside input folder)."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load data + metadata but DO NOT save output file."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists."
    )

    return parser.parse_args()


# -----------------------------
# Main
# -----------------------------
def main():
    print("\033[94m" + "#" * 100 + "\033[0m")
    args = parse_args()
    setup_logging(args)

    input_path = Path(args.input).expanduser().resolve()

    if not input_path.exists():
        log_error(f"Input does not exist: {input_path}")
        sys.exit(1)

    # -------------------------
    # TIFF detection
    # -------------------------
    if input_path.is_dir():
        tiff_paths = find_tiff_files(input_path)
        if not tiff_paths:
            log_error(f"No TIFF files detected in folder: {input_path}")
            sys.exit(1)
        log_info(f"Found {len(tiff_paths)} TIFF files.")
    else:
        # single TIFF
        tiff_paths = [input_path]

    # -------------------------
    # XML detection
    # -------------------------
    xml_path = None
    if args.xml:
        xml_path = Path(args.xml).expanduser().resolve()
        if not xml_path.exists():
            log_error(f"XML file not found: {xml_path}")
            sys.exit(1)
    else:
        # try auto-locate in folder
        possible = list(input_path.parent.glob("Experiment.xml"))
        if possible:
            xml_path = possible[0]
            log_info(f"Auto-detected XML: {xml_path}")
        else:
            log_warn("No Experiment.xml found — continuing without metadata.")

    # -------------------------
    # Load Data with spinner
    # -------------------------
    spinner = Spinner("Loading TIFFs")
    spinner.start()
    try:
        builder = ThorlabBuilder(
            tiff_paths=tiff_paths,
            xml_path=xml_path
        )
        image_data = builder.load()
        metadata = builder.meta
    finally:
        spinner.stop()

    log_info(f"Loaded image stack → shape={image_data.shape}")

    if args.dry_run:
        log_info("Dry-run requested → skipping save.")
        print("Metadata summary:")
        print(metadata)
        return

    out_path = Path(args.output).expanduser().resolve()
    if out_path.exists() and not args.overwrite:
        log_error(f"Output file exists: {out_path} (use --overwrite)")
        sys.exit(1)

    log_info(f"Saving OME-TIFF → {out_path}")
    save_ome_tiff(out_path, image_data, metadata)
    log_done(f"Saved: {out_path}")

    print("\033[94m" + "#" * 100 + "\033[0m")

if __name__ == "__main__":
    main()

