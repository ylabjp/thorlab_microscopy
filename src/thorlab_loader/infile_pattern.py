# src/thorlab_loader/infile_pattern.py
"""
Filename parser for Thorlabs patterns like:
  ChanA_001_001_004_001.tif
Interprets fields:
  channel, stage_x, stage_y, z, t
"""

import re
from pathlib import Path
from typing import Optional, Dict

# Accept 'ChanA' or 'ChA' etc. Keep flexible.
FILENAME_RE = re.compile(
    r"^(?P<channel>Chan[A-Za-z0-9\-]+)_"   # channel prefix
    r"(?P<stage_x>\d+)_"                  # stage X
    r"(?P<stage_y>\d+)_"                  # stage Y
    r"(?P<z>\d+)_"                        # z index
    r"(?P<t>\d+)"                         # t index
    r"(?:\.[^.]+)?$"                      # extension optional
)


def parse_filename(fname: str) -> Optional[Dict]:
    s = Path(fname).name
    m = FILENAME_RE.match(s)
    if not m:
        return None
    gd = m.groupdict()
    try:
        return {
            "filename": s,
            "channel": gd["channel"],
            "stage_x": int(gd["stage_x"]),
            "stage_y": int(gd["stage_y"]),
            "z": int(gd["z"]),
            "t": int(gd["t"]),
        }
    except Exception:
        return None


def parse_or_placeholder(fname: str) -> Dict:
    parsed = parse_filename(fname)
    if parsed:
        return parsed
    return {
        "filename": Path(fname).name,
        "channel": None,
        "stage_x": None,
        "stage_y": None,
        "z": None,
        "t": None,
    }

