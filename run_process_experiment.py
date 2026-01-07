#!/usr/bin/env python3
"""
run_process_experiment.py

Convert Thorlab TIFF + Experiment.xml into OME-TIFF.

This script ONLY works on local files.
Google Drive is handled exclusively in pytest fixtures.
"""

import argparse
import logging
import sys
import time
import datetime
import json
from pathlib import Path

from thorlab_loader.builder import ThorlabBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("thorlab")


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def write_summary(summary: dict, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    summary_path = outdir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary written → {summary_path}")

# --------------------------------------------------
# CLI
# --------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Thorlab TIFF → OME-TIFF converter")

    p.add_argument("--tiff_dir", type=str, required=True,
                   help="Directory containing TIFF files")
    p.add_argument("--xml", type=str, required=True,
                   help="Path to Experiment.xml")

    p.add_argument("--output_dir", type=str, default=None,
                   help="Optional output directory (default: sibling of tiff_dir)")

    p.add_argument("--save_raw", action="store_true",
                   help="Also save raw TIFFs")

    p.add_argument("--verbose", action="store_true")

    return p.parse_args()


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    tiff_dir = Path(args.tiff_dir).resolve()
    xml_path = Path(args.xml).resolve()

    if not tiff_dir.exists():
        sys.exit(f"TIFF directory not found: {tiff_dir}")
    if not xml_path.exists():
        sys.exit(f"Experiment.xml not found: {xml_path}")
    dataset_name = tiff_dir.name
    # Default output logic
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = tiff_dir.parent / f"output_{dataset_name}"

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"TIFF dir   : {tiff_dir}")
    logger.info(f"XML        : {xml_path}")
    logger.info(f"Output dir : {output_dir}")

    start = time.time()
    try:
        builder = ThorlabBuilder(str(tiff_dir), str(xml_path))
        saved_files = builder.run_and_save(str(output_dir), save_raw=args.save_raw)
        status = "sucess"
    except Exception as e:
        logger.exception(f"Failed dataset {dataset_name}")
        saved_files = []
        status = "failed"
        error_msg = str(e)
     
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
        "status": status
    }
    if status == "failed":
        summary["error"] = error_msg

    write_summary(summary, output_dir)    
    logger.info(f"Saved {len(saved_files)} files")


if __name__ == "__main__":
    main()

