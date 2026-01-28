
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

def is_within_radius(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    radius_km: float
) -> bool:
    """
    Check if point 2 is within a given radius of point 1

    Args:
        lat1, lon1: Center point coordinates
        lat2, lon2: Target point coordinates
        radius_km: Radius in kilometers

    Returns:
        True if within radius, False otherwise
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km

def get_bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box (min_lat, max_lat, min_lon, max_lon)
    around a center point for efficient database queries.

    This creates a square approximation for initial filtering before
    applying the precise Haversine distance calculation.

    Args:
        lat: Center latitude
        lon: Center longitude
        radius_km: Radius in kilometers

    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    # Earth's radius in kilometers
    earth_radius = 6371.0

    # Angular distance in radians on a great circle
    angular_distance = radius_km / earth_radius

    # Convert to degrees (rough approximation)
    lat_delta = math.degrees(angular_distance)
    lon_delta = math.degrees(angular_distance / math.cos(math.radians(lat)))

    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta

    return (min_lat, max_lat, min_lon, max_lon)