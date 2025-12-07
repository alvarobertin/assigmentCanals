"""
Database seed script for development and testing.

Run this script to populate the database with sample data:
    python seed_data.py

This creates:
- 3 customers
- 5 products
- 3 warehouses in different US locations
- Varied inventory levels (some products only available in certain warehouses)
"""

from app.database import engine, SessionLocal, Base
from app.models import Customer, Product, Warehouse, Inventory


def seed_database():
    """Seed the database with sample data."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Customer).first():
            print("Database already seeded. Skipping...")
            return
        
        # Create customers
        customers = [
            Customer(id=1, name="Alice Johnson", email="alice@example.com"),
            Customer(id=2, name="Bob Smith", email="bob@example.com"),
            Customer(id=3, name="Carol Williams", email="carol@example.com"),
        ]
        db.add_all(customers)
        
        # Create products
        products = [
            Product(id=1, name="Laptop", price=999.99),
            Product(id=2, name="Wireless Mouse", price=29.99),
            Product(id=3, name="USB-C Hub", price=49.99),
            Product(id=4, name="Monitor Stand", price=79.99),
            Product(id=5, name="Mechanical Keyboard", price=149.99),
        ]
        db.add_all(products)
        
        # Create warehouses in different US locations
        warehouses = [
            Warehouse(
                id=1,
                name="West Coast Warehouse",
                address="123 Tech Blvd, San Francisco, CA 94102, USA",
                latitude=37.7749,
                longitude=-122.4194
            ),
            Warehouse(
                id=2,
                name="Central Warehouse",
                address="456 Commerce St, Dallas, TX 75201, USA",
                latitude=32.7767,
                longitude=-96.7970
            ),
            Warehouse(
                id=3,
                name="East Coast Warehouse",
                address="789 Industrial Ave, New York, NY 10001, USA",
                latitude=40.7128,
                longitude=-74.0060
            ),
        ]
        db.add_all(warehouses)
        
        # Create inventory with varied stock levels
        # West Coast: Has all products, good stock
        # Central: Missing product 5 (Mechanical Keyboard)
        # East Coast: Has all products but limited stock on some
        inventory = [
            # West Coast Warehouse (id=1) - Full stock
            Inventory(warehouse_id=1, product_id=1, quantity=50),   # Laptop
            Inventory(warehouse_id=1, product_id=2, quantity=200),  # Mouse
            Inventory(warehouse_id=1, product_id=3, quantity=150),  # USB-C Hub
            Inventory(warehouse_id=1, product_id=4, quantity=100),  # Monitor Stand
            Inventory(warehouse_id=1, product_id=5, quantity=75),   # Keyboard
            
            # Central Warehouse (id=2) - Missing Keyboard
            Inventory(warehouse_id=2, product_id=1, quantity=30),   # Laptop
            Inventory(warehouse_id=2, product_id=2, quantity=250),  # Mouse
            Inventory(warehouse_id=2, product_id=3, quantity=100),  # USB-C Hub
            Inventory(warehouse_id=2, product_id=4, quantity=80),   # Monitor Stand
            # No Keyboard!
            
            # East Coast Warehouse (id=3) - Limited laptop stock
            Inventory(warehouse_id=3, product_id=1, quantity=5),    # Laptop (low)
            Inventory(warehouse_id=3, product_id=2, quantity=300),  # Mouse
            Inventory(warehouse_id=3, product_id=3, quantity=200),  # USB-C Hub
            Inventory(warehouse_id=3, product_id=4, quantity=120),  # Monitor Stand
            Inventory(warehouse_id=3, product_id=5, quantity=50),   # Keyboard
        ]
        db.add_all(inventory)
        
        db.commit()
        print("Database seeded successfully!")
        print(f"  - {len(customers)} customers")
        print(f"  - {len(products)} products")
        print(f"  - {len(warehouses)} warehouses")
        print(f"  - {len(inventory)} inventory entries")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

