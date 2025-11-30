# src/thorlab_loader/utils.py
import re
from pathlib import Path
from typing import List
import logging

def natural_sort_key(s: str):
    parts = re.split(r"(\d+)", s)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

def find_tiff_files(folder: str) -> List[str]:
    p = Path(folder)
    if not p.exists():
        raise FileNotFoundError(f"Input folder not found: {folder}")
    files = []
    for ext in ("*.tif", "*.tiff"):
        files.extend(list(p.glob(ext)))
    files = sorted(files, key=lambda x: natural_sort_key(x.name))
    return [str(x.resolve()) for x in files]

def count_files_in_directory(directory_path):
    path = Path(directory_path)
    count = len([p for p in path.iterdir() if p.is_file()])
    return count

# Simple colored logs
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
    logging.done(f"\033[92m[DONE]\033[0m {msg}")


def log_warn(msg):
    logging.warning(f"\033[93m[WARN]\033[0m {msg}")


def log_error(msg):
    logging.error(f"\033[91m[ERROR]\033[0m {msg}")

def ensure_parent(path: str):
    Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

