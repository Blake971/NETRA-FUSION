"""
Geographic clustering and validation using Haversine distance.
"""

import math
from typing import List, Tuple, Optional


class GeographicValidator:
    """Validates geographic consistency using coordinate clustering."""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth.
        Returns distance in kilometers.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in kilometers
        r = 6371
        return c * r
    
    @staticmethod
    def calculate_cluster_stats(coordinates: List[Tuple[float, float]]) -> dict:
        """
        Calculate statistics for a cluster of coordinates.
        Returns average lat/lon, standard deviation, and consensus radius.
        """
        if not coordinates:
            return {
                'avg_lat': None,
                'avg_lon': None,
                'std_dev': None,
                'consensus_radius': None,
                'max_distance': None
            }
        
        if len(coordinates) == 1:
            return {
                'avg_lat': coordinates[0][0],
                'avg_lon': coordinates[0][1],
                'std_dev': 0.0,
                'consensus_radius': 0.0,
                'max_distance': 0.0
            }
        
        # Calculate average
        avg_lat = sum(c[0] for c in coordinates) / len(coordinates)
        avg_lon = sum(c[1] for c in coordinates) / len(coordinates)
        
        # Calculate distances from average
        distances = [GeographicValidator.haversine_distance(avg_lat, avg_lon, c[0], c[1]) 
                     for c in coordinates]
        
        # Calculate standard deviation
        if len(distances) > 1:
            mean_dist = sum(distances) / len(distances)
            variance = sum((d - mean_dist) ** 2 for d in distances) / len(distances)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0
        
        return {
            'avg_lat': avg_lat,
            'avg_lon': avg_lon,
            'std_dev': std_dev,
            'consensus_radius': max(distances) if distances else 0.0,
            'max_distance': max(distances) if distances else 0.0
        }
    
    @staticmethod
    def validate_coordinates(lat: Optional[float], lon: Optional[float]) -> bool:
        """Validate that coordinates are within valid ranges."""
        if lat is None or lon is None:
            return False
        
        return -90 <= lat <= 90 and -180 <= lon <= 180
