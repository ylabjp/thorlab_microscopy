from pathlib import Path
from datetime import datetime
import pandas as pd


def build_output_name(output_dir: Path, tiff_files, Z_stack_val, T_stack_val):

    records = []

    for f in tiff_files:

        name = Path(f).name

        parts = name.replace(".tif","").replace(".tiff","").split("_")

        channel = None
        stageX = None
        stageY = None
        z = None
        t = None

        for p in parts:
            if "Chan" in p or "CH" in p:
                channel = p

        try:
            stageX = int(parts[2])
            stageY = int(parts[3])
            z = int(parts[4])
        except:
            pass

        records.append({
            "path": f,
            "filename": name,
            "channel": channel,
            "stageX": stageX,
            "stageY": stageY,
            "z": z,
            "t": t,
        })

    df = pd.DataFrame(records)

    if df is None or len(df) == 0:
        raise RuntimeError("Metadata dataframe empty — cannot build output name")

    ch = df["channel"].dropna().iloc[0]
    ''''
    zvals = df["z"].dropna().astype(int).sort_values().unique()
    num_z = len(zvals)

    if num_z == 0:
        zpart = "Zsingle"
    elif num_z == 1:
        zpart = f"Z{zvals[0]:03d}_stack"
    else:
        z_min = zvals.min()
        z_max = zvals.max()
        zpart = f"Zstack_{z_min:03d}to{z_max:03d}"

    stageX = df["stageX"].dropna().iloc[0] if not df["stageX"].empty else 0
    stageY = df["stageY"].dropna().iloc[0] if not df["stageY"].empty else 0
    tval = df["t"].dropna().iloc[0] if df["t"].notna().any() else 1

    filename = f"Output_{ch}_X{stageX:03d}_Y{stageY:03d}_{zpart}_T{tval:03d}"
    '''

    total_z = Z_stack_val
    z_start = int(df["z"].dropna().min()) if not df.get("z", pd.Series()).empty else 1
    
    if total_z > 1:
        zpart = f"Z{z_start:03d}_stack{total_z}"
    else:
        zpart = f"Z{z_start:03d}"

    total_t = T_stack_val
    t_start = int(df["t"].dropna().min()) if "t" in df.columns and not df["t"].dropna().empty else 1
    
    if total_t > 1:
        tpart = f"T{t_start:03d}_series{total_t}"
    else:
        tpart = f"T{t_start:03d}"

    filename = f"Output_{ch}_X{stageX:03d}_Y{stageY:03d}_{zpart}_{tpart}"

    return output_dir / filename

