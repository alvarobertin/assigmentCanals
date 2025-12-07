import math
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models import Warehouse, Inventory
from app.services.geocoding import GeoLocation


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.
    
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(delta_lat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def find_best_warehouse(
    db: Session,
    items: list[tuple[int, int]],  # List of (product_id, quantity)
    shipping_location: GeoLocation
) -> Warehouse | None:
    """
    Find the best warehouse to fulfill an order.
    
    A warehouse must have ALL requested products in sufficient quantity.
    If multiple warehouses qualify, returns the one closest to the shipping address.
    
    Args:
        db: Database session
        items: List of (product_id, quantity) tuples
        shipping_location: Geocoded shipping address
        
    Returns:
        The best warehouse, or None if no warehouse can fulfill the order
    """
    if not items:
        return None
    
    num_products = len(items)
    
    # Build conditions for each product with its required quantity
    # Each condition checks: product_id matches AND quantity is sufficient
    conditions = [
        and_(
            Inventory.product_id == product_id,
            Inventory.quantity >= qty
        )
        for product_id, qty in items
    ]
    
    # Single query to find warehouses with ALL products in sufficient quantity:
    # 1. Join Inventory with Warehouse
    # 2. Filter: inventory matches ANY of our (product_id, quantity) conditions
    # 3. Group by warehouse_id
    # 4. HAVING: count of matching products equals total required products
    #    (ensures warehouse has ALL products, not just some)
    qualifying_warehouse_ids = (
        db.query(Inventory.warehouse_id)
        .filter(or_(*conditions))
        .group_by(Inventory.warehouse_id)
        .having(func.count(Inventory.product_id) == num_products)
        .all()
    )
    
    if not qualifying_warehouse_ids:
        return None
    
    # Extract IDs from result tuples
    warehouse_ids = [row[0] for row in qualifying_warehouse_ids]
    
    # Get warehouse details
    warehouses = db.query(Warehouse).filter(
        Warehouse.id.in_(warehouse_ids)
    ).all()
    
    if not warehouses:
        return None
    
    # If only one warehouse qualifies, return it
    if len(warehouses) == 1:
        return warehouses[0]
    
    # Multiple warehouses qualify - find the closest one
    best_warehouse = None
    best_distance = float('inf')
    
    for warehouse in warehouses:
        distance = haversine_distance(
            shipping_location.latitude,
            shipping_location.longitude,
            warehouse.latitude,
            warehouse.longitude
        )
        if distance < best_distance:
            best_distance = distance
            best_warehouse = warehouse
    
    return best_warehouse

