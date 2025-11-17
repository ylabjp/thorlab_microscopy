# src/thorlab_loader/utils.py

import os


def ensure_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")


def ensure_list(x):
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

