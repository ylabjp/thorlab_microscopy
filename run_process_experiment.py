#!/usr/bin/env python3
"""
run_process_experiment.py
"""

import argparse
import logging
from pathlib import Path
import sys

from thorlab_loader.builder import ThorlabBuilder
from thorlab_loader.download_drive_folder import download_and_extract_drive_folder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("thorlab_pipeline")


def parse_args():
    p = argparse.ArgumentParser(description="Thorlab: local or Google Drive TIFF/XML processing")

    # Local mode
    p.add_argument("--tiff_dir", type=str)
    p.add_argument("--xml", type=str)

    # Drive mode
    p.add_argument("--drive_folder", type=str)
    p.add_argument("--auth_mode", choices=["service_account", "oauth"], default="service_account")
    p.add_argument("--service_account", type=str, help="Path to service_account.json")
    p.add_argument("--client_secret", type=str, help="Path to client_secret.json")

    # Directories
    p.add_argument("--work_dir", type=str, default="./drive_work")
    p.add_argument("--output_dir", type=str, default="./output")

    p.add_argument("--save_raw", action="store_true")
    p.add_argument("--verbose", action="store_true")

    return p.parse_args()


# ----------------------------------------------
# LOCAL MODE
# ----------------------------------------------

def process_local_mode(tiff_dir: Path, xml_path: Path, output_dir: Path, save_raw: bool):
    logger.info(f"Processing local dataset: {tiff_dir}")

    builder = ThorlabBuilder(str(tiff_dir), str(xml_path))
    saved = builder.run_and_save(str(output_dir), save_raw=save_raw)

    logger.info(f"Local processing complete — saved {len(saved)} files → {output_dir}")


# ----------------------------------------------
# DRIVE MODE
# ----------------------------------------------

def process_drive_mode(folder_url: str, auth_mode: str, work_dir: Path,
                       service_account_path: str, client_secret_path: str,
                       output_root: Path, save_raw: bool):

    logger.info(f"Drive mode: downloading from: {folder_url}")

    extracted_root = download_and_extract_drive_folder(
        folder_url=folder_url,
        work_dir=work_dir,
        auth_mode=auth_mode,
        service_account_json=service_account_path,
        client_secret_json=client_secret_path,
    )

    logger.info(f"Extracted root: {extracted_root}")

    # find individual datasets
    datasets = [d for d in extracted_root.iterdir() if d.is_dir()]

    if not datasets:
        raise FileNotFoundError("No extracted datasets found.")

    for dataset in datasets:
        xml_path = next(dataset.rglob("Experiment.xml"), None)
        if xml_path is None:
            logger.warning(f"No XML inside {dataset}, skipping.")
            continue

        dataset_output = output_root.parent / f"output_{dataset.name}"
        dataset_output.mkdir(parents=True, exist_ok=True)

        logger.info(f"Processing {dataset.name} → {dataset_output}")

        builder = ThorlabBuilder(str(dataset), str(xml_path))
        saved = builder.run_and_save(str(dataset_output), save_raw=save_raw)

        logger.info(f"{dataset.name}: saved {len(saved)} files.")


# ----------------------------------------------
# MAIN
# ----------------------------------------------

def main():
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    # Validation
    if args.drive_folder and (args.tiff_dir or args.xml):
        sys.exit("Use either local mode OR drive mode, not both.")

    if args.tiff_dir and not args.xml:
        sys.exit("--xml required when using --tiff_dir")

    if not args.drive_folder and not args.tiff_dir:
        sys.exit("Must use either --drive_folder OR --tiff_dir + --xml")

    # LOCAL MODE
    if args.tiff_dir:
        return process_local_mode(
            Path(args.tiff_dir).resolve(),
            Path(args.xml).resolve(),
            output_root,
            args.save_raw,
        )

    # DRIVE MODE
    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    return process_drive_mode(
        folder_url=args.drive_folder,
        auth_mode=args.auth_mode,
        work_dir=work_dir,
        service_account_path=args.service_account,
        client_secret_path=args.client_secret,
        output_root=output_root,
        save_raw=args.save_raw,
    )


if __name__ == "__main__":
    main()

