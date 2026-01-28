
import math
from typing import Tuple, Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
        lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)

    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers
    radius = 6371.0

    distance = radius * c
    return round(distance, 2)

