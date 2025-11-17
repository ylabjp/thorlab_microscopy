import tifffile

def save_ome_tiff(output_path, arr, meta, compress=False):

    # --- Promote input to 5D (T,C,Z,Y,X) ---
    if arr.ndim == 3:          # (Z, Y, X)
        arr5 = arr[None, None]  # (1,1,Z,Y,X)
    elif arr.ndim == 4:        # (C, Z, Y, X)
        arr5 = arr[None]        # (1,C,Z,Y,X)
    elif arr.ndim == 5:
        arr5 = arr
    else:
        raise ValueError(f"Unsupported shape {arr.shape}")

    T, C, Z, Y, X = arr5.shape

    # --- Ensure channel names exist ---
    channel_names = meta.channel_names or []
    if len(channel_names) < C:
        channel_names = [f"Channel_{i+1}" for i in range(C)]

    # --- Construct metadata ---
    ome_meta = {
        "axes": "TCZYX",
        "SizeT": T,
        "SizeC": C,
        "SizeZ": Z,
        "SizeY": Y,
        "SizeX": X,
        "PhysicalSizeX": meta.physical_size_x,
        "PhysicalSizeY": meta.physical_size_y,
        "PhysicalSizeZ": meta.physical_size_z,
        "PhysicalSizeXUnit": "µm",
        "PhysicalSizeYUnit": "µm",
        "PhysicalSizeZUnit": "µm",
        "Channel": [{"Name": ch} for ch in channel_names],
    }

    # --- Write ---
    tifffile.imwrite(
        output_path,
        arr5,
        metadata=ome_meta,
        ome=True,
        compression="lzma" if compress else None,
    )

    print(f"[OK] Saved OME-TIFF → {output_path}")
    print(f"     Shape={arr5.shape}, axes=TCZYX")

