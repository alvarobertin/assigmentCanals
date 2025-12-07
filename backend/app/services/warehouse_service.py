import math
from sqlalchemy import func
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
    
    product_ids = [item[0] for item in items]
    required_quantities = {item[0]: item[1] for item in items}
    num_products = len(product_ids)
    
    # Find warehouses that have ALL products with sufficient quantity
    # We do this by:
    # 1. Filtering inventory entries for the requested products with enough stock
    # 2. Grouping by warehouse
    # 3. Counting distinct products - must equal total requested products
    
    # Subquery to get warehouses with sufficient stock for each product
    qualifying_inventory = (
        db.query(Inventory.warehouse_id, Inventory.product_id)
        .filter(Inventory.product_id.in_(product_ids))
    ).all()
    
    # Group by warehouse and check which ones have all products with sufficient qty
    warehouse_products: dict[int, list[int]] = {}
    for warehouse_id, product_id in qualifying_inventory:
        # Get the actual inventory entry to check quantity
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.product_id == product_id
        ).first()
        
        if inv and inv.quantity >= required_quantities[product_id]:
            if warehouse_id not in warehouse_products:
                warehouse_products[warehouse_id] = []
            warehouse_products[warehouse_id].append(product_id)
    
    # Find warehouses that have ALL products
    qualifying_warehouse_ids = [
        wh_id for wh_id, products in warehouse_products.items()
        if len(products) == num_products
    ]
    
    if not qualifying_warehouse_ids:
        return None
    
    # Get warehouse details
    warehouses = db.query(Warehouse).filter(
        Warehouse.id.in_(qualifying_warehouse_ids)
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

