import math
from typing import Tuple, Union

# Earth’s mean radius in meters (per WGS-84 average)
EarthRadius: float = (((2 * 6_378.1370) + 6_356.7523) / 3) * 1_000  

Numeric = Union[int, float]

def latlon_to_local_xy(
    lat: Numeric,
    lon: Numeric,
    ref_lat: Numeric,
    ref_lon: Numeric,
    radius: float = EarthRadius
) -> Tuple[float, float]:
    """
    Convert geographic coordinates (lat, lon) in degrees to local tangent-plane 
    coordinates (x, y) in meters, relative to (ref_lat, ref_lon).

    Preconditions:
      - lat, lon, ref_lat, ref_lon are numeric.
      - radius > 0.
    Postconditions:
      - Returns x, y in meters (can be negative for West/South).
    """
    # Preconditions
    for name, val in (("lat", lat), ("lon", lon),
                      ("ref_lat", ref_lat), ("ref_lon", ref_lon)):
        assert isinstance(val, (int, float)), f"{name} must be numeric."
    assert radius > 0, "radius must be positive."

    # Convert to radians
    φ  = math.radians(lat)
    λ  = math.radians(lon)
    φ0 = math.radians(ref_lat)
    λ0 = math.radians(ref_lon)

    # Equirectangular approximation
    x = (λ - λ0) * math.cos((φ + φ0) / 2.0) * radius
    y = (φ - φ0) * radius

    return x, y


def local_to_latlon(
    x: Numeric,
    y: Numeric,
    ref_lat: Numeric,
    ref_lon: Numeric,
    radius: float = EarthRadius
) -> Tuple[float, float]:
    """
    Convert local tangent-plane coordinates (x, y) in meters back to
    geographic coordinates (lat, lon) in degrees, relative to (ref_lat, ref_lon).

    Preconditions:
      - x, y are numeric.
      - ref_lat, ref_lon are numeric.
      - radius > 0.
    Postconditions:
      - Returns (lat, lon) in degrees.
    """
    # Preconditions
    for name, val in (("x", x), ("y", y),
                      ("ref_lat", ref_lat), ("ref_lon", ref_lon)):
        assert isinstance(val, (int, float)), f"{name} must be numeric."
    assert radius > 0, "radius must be positive."

    φ0 = math.radians(ref_lat)

    # Inverse equirectangular
    delta_lat = y / radius
    delta_lon = x / (radius * math.cos(φ0))

    lat = ref_lat + math.degrees(delta_lat)
    lon = ref_lon + math.degrees(delta_lon)

    return lat, lon