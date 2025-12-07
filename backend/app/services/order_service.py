from sqlalchemy.orm import Session

from app.models import Customer, Product, Order, OrderItem
from app.schemas import CreateOrderRequest, OrderResponse, OrderItemResponse, WarehouseResponse
from app.services.geocoding import geocode_address
from app.services.warehouse_service import find_best_warehouse
from app.services.payment import process_payment


class OrderServiceError(Exception):
    """Base exception for order service errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class CustomerNotFoundError(OrderServiceError):
    def __init__(self, customer_id: int):
        super().__init__(f"Customer with id {customer_id} not found", 404)


class ProductNotFoundError(OrderServiceError):
    def __init__(self, product_ids: list[int]):
        ids_str = ", ".join(str(id) for id in product_ids)
        super().__init__(f"Products not found: {ids_str}", 404)


class NoWarehouseAvailableError(OrderServiceError):
    def __init__(self):
        super().__init__(
            "No warehouse has all requested products in sufficient quantity",
            400
        )


class PaymentFailedError(OrderServiceError):
    def __init__(self, message: str):
        super().__init__(f"Payment failed: {message}", 402)


def create_order(db: Session, request: CreateOrderRequest) -> OrderResponse:
    """
    Create a new order.
    
    This function orchestrates the full order creation process:
    1. Validate customer exists
    2. Validate products and get prices
    3. Geocode shipping address
    4. Find best warehouse
    5. Process payment
    6. Create order in database
    
    Raises:
        CustomerNotFoundError: If customer doesn't exist
        ProductNotFoundError: If any product doesn't exist
        NoWarehouseAvailableError: If no warehouse can fulfill the order
        PaymentFailedError: If payment processing fails
    """
    # 1. Validate customer exists
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise CustomerNotFoundError(request.customer_id)
    
    # 2. Validate products and get prices
    product_ids = [item.product_id for item in request.items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    products_map = {p.id: p for p in products}
    
    missing_products = [pid for pid in product_ids if pid not in products_map]
    if missing_products:
        raise ProductNotFoundError(missing_products)
    
    # 3. Geocode shipping address
    shipping_address_str = request.shipping_address.to_string()
    geo_location = geocode_address(shipping_address_str)
    
    # 4. Find best warehouse
    items_with_qty = [(item.product_id, item.quantity) for item in request.items]
    warehouse = find_best_warehouse(db, items_with_qty, geo_location)
    
    if not warehouse:
        raise NoWarehouseAvailableError()
    
    # 5. Calculate total amount
    total_amount = sum(
        products_map[item.product_id].price * item.quantity
        for item in request.items
    )
    
    # 6. Process payment
    payment_description = f"Order for customer {customer.id}: {len(request.items)} items"
    payment_result = process_payment(
        card_number=request.credit_card.number,
        amount=total_amount,
        description=payment_description
    )
    
    if not payment_result.success:
        raise PaymentFailedError(payment_result.error_message or "Unknown error")
    
    # 7. Create order in database (within transaction)
    order = Order(
        customer_id=request.customer_id,
        warehouse_id=warehouse.id,
        shipping_address=shipping_address_str,
        shipping_lat=geo_location.latitude,
        shipping_lng=geo_location.longitude,
        total_amount=total_amount,
        payment_id=payment_result.payment_id,
        status="confirmed"
    )
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items
    order_items = []
    for item in request.items:
        product = products_map[item.product_id]
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.price
        )
        db.add(order_item)
        order_items.append(order_item)
    
    db.commit()
    db.refresh(order)
    
    # 8. Build response
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        warehouse=WarehouseResponse(
            id=warehouse.id,
            name=warehouse.name,
            address=warehouse.address
        ),
        shipping_address=order.shipping_address,
        total_amount=order.total_amount,
        payment_id=order.payment_id,
        status=order.status,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=products_map[item.product_id].name,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in order_items
        ]
    )

