import hashlib
from dataclasses import dataclass


@dataclass
class GeoLocation:
    latitude: float
    longitude: float


def geocode_address(address: str) -> GeoLocation:
    """
    Mock geocoding service that converts an address to latitude/longitude.
    
    Uses a deterministic hash-based approach to generate consistent coordinates
    for the same address. Maps to valid US continental coordinates range.
    
    In production, this would call a 3rd party geocoding API like Google Maps,
    Mapbox, or OpenStreetMap Nominatim.
    """
    # Create a deterministic hash from the address
    address_hash = hashlib.sha256(address.lower().encode()).hexdigest()
    
    # Use first 8 hex chars for latitude, next 8 for longitude
    lat_hash = int(address_hash[:8], 16)
    lng_hash = int(address_hash[8:16], 16)
    
    # Map to US continental coordinates range
    # Latitude: 25 to 49 (southern tip of Florida to Canadian border)
    # Longitude: -125 to -67 (West coast to East coast)
    max_val = 0xFFFFFFFF
    
    latitude = 25 + (lat_hash / max_val) * 24  # 25 to 49
    longitude = -125 + (lng_hash / max_val) * 58  # -125 to -67
    
    return GeoLocation(latitude=round(latitude, 6), longitude=round(longitude, 6))

