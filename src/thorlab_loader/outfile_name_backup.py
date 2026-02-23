from pathlib import Path
import pandas as pd


def validate_and_cast(label, value):
    if value is None:
        raise ValueError(f"{label} is None — cannot build output name")

    try:
        return int(value)
    except Exception:
        raise ValueError(f"{label} value '{value}' is not castable to int")

def build_output_name(self, df):

    """
    Build scientific output filename based on
    channel / stage position / Z range / time index.

    Example:
    Output_ChanA_001_001_merged_001To080_001
    """

    if df is None or len(df) == 0:
        raise RuntimeError("Metadata dataframe empty — cannot build output name")
    
    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # channel
    ch = df["channel"].dropna().iloc[0]

    # stage positions
    sx = int(df["stage_x"].dropna().iloc[0])
    sy = int(df["stage_y"].dropna().iloc[0])

    # time index
    t = int(df["t"].dropna().iloc[0])

    # Z range
    zvals = (
        df["z"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
    )

    if len(zvals) == 0:
        zpart = "Zsingle"

    elif len(zvals) == 1:
        zpart = f"Z{zvals[0]:03d}"

    else:
        zpart = f"merged_{zvals.min():03d}To{zvals.max():03d}"

    base_name = f"Output_{ch}_{sx:03d}_{sy:03d}_{zpart}_{t:03d}"

    return self.output_dir / base_name

