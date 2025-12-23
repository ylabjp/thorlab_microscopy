#!/usr/bin/env python3
"""
run_process_experiment.py

Supports:
 - Local mode  : --tiff_dir + --xml
 - Drive mode  : --drive_folder

Output handling:
 - Local default  : <tiff_dir.parent>/output_<dataset>
 - Drive default  : <extracted_root>/output_<dataset>
 - Override       : --diff_outdirpath
"""

import argparse
import json
import logging
import sys
import time
import threading
from pathlib import Path
import datetime

from thorlab_loader.builder import ThorlabBuilder
from thorlab_loader.download_drive_folder import download_and_extract_drive_folder
from thorlab_loader.utils import log_info, log_done, log_warn, log_error

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("thorlab_runner")

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


# -------------------------------------------------
# CLI
# -------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser("Thorlab microscopy processor")

    # Local mode
    p.add_argument("--tiff_dir", type=str)
    p.add_argument("--xml", type=str)

    # Drive mode
    p.add_argument("--drive_folder", type=str)
    p.add_argument("--auth_mode", choices=["service_account", "oauth"], default="service_account")
    p.add_argument("--service_account", type=str)
    p.add_argument("--client_secret", type=str)

    # Directories
    p.add_argument("--work_dir", type=str, default="./drive_work")
    p.add_argument("--output_dir", type=str, default="./output")  # kept for backward compatibility
    p.add_argument(
        "--diff_outdirpath",
        type=str,
        default=None,
        help="Optional different base output directory"
    )

    p.add_argument("--save_raw", action="store_true")
    p.add_argument("--verbose", action="store_true")

    return p.parse_args()


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def write_summary(summary: dict, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    summary_path = outdir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary written → {summary_path}")


# -------------------------------------------------
# LOCAL MODE
# -------------------------------------------------
def process_local_mode(tiff_dir: Path, xml_path: Path, args):
    logger.info("Running in LOCAL mode")

    dataset_name = tiff_dir.name

    if args.diff_outdirpath:
        output_dir = Path(args.diff_outdirpath) / f"output_{dataset_name}"
    else:
        output_dir = tiff_dir.parent / f"output_{dataset_name}"

    output_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()

    builder = ThorlabBuilder(str(tiff_dir), str(xml_path))
    saved_files = builder.run_and_save(str(output_dir), save_raw=args.save_raw)

    elapsed = time.time() - start

    summary = {
        "mode": "local",
        "dataset": dataset_name,
        "tiff_dir": str(tiff_dir),
        "xml": str(xml_path),
        "output_dir": str(output_dir),
        "n_files_written": len(saved_files),
        "runtime_sec": round(elapsed, 2),
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    write_summary(summary, output_dir)


# -------------------------------------------------
# DRIVE MODE
# -------------------------------------------------
def process_drive_mode(args):
    logger.info("Running in DRIVE mode")

    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    extracted_root = download_and_extract_drive_folder(
        folder_url=args.drive_folder,
        work_dir=work_dir,
        auth_mode=args.auth_mode,
        service_account_json=args.service_account,
        client_secret_json=args.client_secret,
    )

    datasets = [p for p in extracted_root.iterdir() if p.is_dir()]
    logger.info(f"Found {len(datasets)} extracted datasets")

    for dataset in datasets:
        xml_files = list(dataset.glob("**/Experiment.xml"))
        if not xml_files:
            logger.warning(f"No Experiment.xml found in {dataset}, skipping")
            continue

        xml_path = xml_files[0]
        dataset_name = dataset.name

        if args.diff_outdirpath:
            output_dir = Path(args.diff_outdirpath) / f"output_{dataset_name}"
        else:
            output_dir = extracted_root / f"output_{dataset_name}"

        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Processing dataset: {dataset_name}")
        start = time.time()

        try:
            builder = ThorlabBuilder(str(dataset), str(xml_path))
            saved_files = builder.run_and_save(str(output_dir), save_raw=args.save_raw)
            status = "success"
        except Exception as e:
            logger.exception(f"Failed dataset {dataset_name}")
            saved_files = []
            status = "failed"
            error_msg = str(e)

        elapsed = time.time() - start

        summary = {
            "mode": "drive",
            "dataset": dataset_name,
            "input_dir": str(dataset),
            "xml": str(xml_path),
            "output_dir": str(output_dir),
            "n_files_written": len(saved_files),
            "runtime_sec": round(elapsed, 2),
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": status,
        }

        if status == "failed":
            summary["error"] = error_msg

        write_summary(summary, output_dir)


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    print("\033[94m" + "#" * 100 + "\033[0m")
    spinner = Spinner("")
    spinner.start()
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validation
    if args.drive_folder and (args.tiff_dir or args.xml):
        sys.exit("Use either local mode OR drive mode, not both.")

    if args.tiff_dir and not args.xml:
        sys.exit("--xml is required with --tiff_dir")

    if not args.drive_folder and not args.tiff_dir:
        sys.exit("Must use either --drive_folder OR --tiff_dir + --xml")

    if args.tiff_dir:
        process_local_mode(
            Path(args.tiff_dir).resolve(),
            Path(args.xml).resolve(),
            args,
        )
    else:
        process_drive_mode(args)
    spinner.stop()
    print("\033[94m" + "#" * 100 + "\033[0m")

if __name__ == "__main__":
    main()

