from dataclasses import dataclass

@dataclass
class ValidationConfig:
    pixel_size_tol: float = 1e-6        # µm tolerance
    time_interval_tol: float = 1e-3     # seconds
    allow_axis_permutation: bool = True
    strict_dimensions: bool = True      # fail if XYZ mismatch
    strict_channels: bool = True

