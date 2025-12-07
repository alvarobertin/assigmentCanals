from datetime import datetime
from pydantic import BaseModel, Field


# Request schemas
class ShippingAddress(BaseModel):
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    zip: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)

    def to_string(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip}, {self.country}"


class CreditCard(BaseModel):
    number: str = Field(..., min_length=13, max_length=19)
    expiry: str = Field(..., pattern=r"^\d{2}/\d{2}$")
    cvv: str = Field(..., min_length=3, max_length=4)


class OrderItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CreateOrderRequest(BaseModel):
    customer_id: int = Field(..., gt=0)
    shipping_address: ShippingAddress
    credit_card: CreditCard
    items: list[OrderItemRequest] = Field(..., min_length=1)


# Response schemas
class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class WarehouseResponse(BaseModel):
    id: int
    name: str
    address: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    warehouse: WarehouseResponse
    shipping_address: str
    total_amount: float
    payment_id: str
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str

