from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

    inventory_items = relationship("Inventory", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    inventory_items = relationship("Inventory", back_populates="warehouse")
    orders = relationship("Order", back_populates="warehouse")


class Inventory(Base):
    __tablename__ = "inventory"

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)

    warehouse = relationship("Warehouse", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    shipping_address = Column(Text, nullable=False)
    shipping_lat = Column(Float, nullable=False)
    shipping_lng = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="confirmed")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    warehouse = relationship("Warehouse", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

