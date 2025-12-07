from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CreateOrderRequest, OrderResponse, ErrorResponse
from app.services.order_service import (
    create_order,
    OrderServiceError,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "No warehouse available"},
        402: {"model": ErrorResponse, "description": "Payment failed"},
        404: {"model": ErrorResponse, "description": "Customer or product not found"},
    }
)
def create_order_endpoint(
    request: CreateOrderRequest,
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    Create a new order.
    
    This endpoint creates an order by:
    1. Validating the customer exists
    2. Validating all products exist
    3. Finding the best warehouse (one with all items, closest to shipping address)
    4. Processing payment
    5. Creating the order
    
    The order will be fulfilled from a single warehouse that has all requested
    products in sufficient quantity. If multiple warehouses qualify, the closest
    one to the shipping address is selected.
    """
    try:
        return create_order(db, request)
    except OrderServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

