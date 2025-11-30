#!/usr/bin/env python3
import argparse
import logging
import threading
import time
import sys
from pathlib import Path
from thorlab_loader.builder import ThorlabBuilder
from thorlab_loader.utils import log_info, log_done, log_warn, log_error

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





def parse_args():
    parser = argparse.ArgumentParser(description="Process Thorlabs TIFF folder (Experiment.xml required)")

    parser.add_argument(
        "--tiff_dir", "-i", 
        required=True, 
        help="Folder containing TIFF files"
    )
    parser.add_argument(
        "--xml", "-x", 
        required=True, 
        help="Experiment.xml path (required)"
    )
    parser.add_argument(
        "--output_dir", "-o", 
        required=True, 
        help="Output directory for generated TIFFs"
    )
    parser.add_argument(
        "--save_raw", 
        action="store_true", 
        help="Also save plain multi-page TIFF alongside OME"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose logs"
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
    return parser.parse_args()

def main():
    print("\033[94m" + "#" * 100 + "\033[0m")
    args = parse_args()
    #logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s - %(message)s")
    setup_logging(args)
    spinner = Spinner("Loading TIFFs")
    spinner.start()
    tiff_dir = Path(args.tiff_dir).expanduser().resolve()
    xml_path = Path(args.xml).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    spinner.stop()

    tiff_files = sorted([p for p in tiff_dir.glob("Chan*.tif")])
    print(f"[INFO] Loaded {len(tiff_files)} Chan*.tif files")

    builder = ThorlabBuilder(str(tiff_dir), str(xml_path))
    saved = builder.run_and_save(str(out_dir), save_raw=args.save_raw)
    if args.dry_run:
        log_info("Dry-run requested → skipping save.")
        print("Metadata summary:")
        print(metadata)
        return

    log_done(f"Saved {len(saved)} files to {out_dir}")
    print("\033[94m" + "#" * 100 + "\033[0m")

if __name__ == "__main__":
    main()

