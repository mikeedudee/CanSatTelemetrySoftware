# geo_utils.py

"""
Module: geo_utils
Provides geodetic utility functions.
Adheres to “Power of Ten” guidelines: small, well-documented, and defensively coded.
"""

import math
from typing import Union

# Earth’s mean radius in meters (per WGS-84 average)
EarthRadius: float = (((2 * 6_378.1370) + 6_356.7523) / 3) * 1_000  

def haversine_distance(
    lat1: Union[float,int],
    lon1: Union[float,int],
    lat2: Union[float,int],
    lon2: Union[float,int],
    radius: float = EarthRadius
) -> float:
    """
    Calculate the great-circle distance between two points on a sphere 
    using the haversine formula.

    Preconditions:
      - lat1, lon1, lat2, lon2 are in decimal degrees.
      - radius > 0.

    Postconditions:
      - returns non-negative distance in meters.

    Raises:
      - AssertionError if inputs are invalid.
    """
    # Preconditions
    for name, val in (("lat1", lat1), ("lon1", lon1), 
                      ("lat2", lat2), ("lon2", lon2)):
        assert isinstance(val, (int, float)), f"{name} must be numeric."
    assert radius > 0, "radius must be positive."

    # Convert to radians
    φ1, λ1, φ2, λ2 = map(math.radians, (lat1, lon1, lat2, lon2))

    # Haversine
    dφ = φ2 - φ1
    dλ = λ2 - λ1
    a  = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    c  = 2 * math.asin(math.sqrt(a))

    distance = radius * c

    # Postcondition
    assert distance >= 0, "Computed distance is negative."
    return distance
