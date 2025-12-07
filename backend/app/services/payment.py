import uuid
from dataclasses import dataclass


@dataclass
class PaymentResult:
    success: bool
    payment_id: str | None
    error_message: str | None


def process_payment(card_number: str, amount: float, description: str) -> PaymentResult:
    """
    Mock payment gateway that processes credit card payments.
    
    Simulates payment processing with the following behavior:
    - Cards starting with "0" are declined (for testing failure scenarios)
    - All other cards are approved
    
    In production, this would integrate with a payment processor like Stripe,
    Braintree, or Adyen using their secure tokenization APIs.
    """
    # Simulate payment validation
    if not card_number or len(card_number) < 13:
        return PaymentResult(
            success=False,
            payment_id=None,
            error_message="Invalid card number"
        )
    
    if amount <= 0:
        return PaymentResult(
            success=False,
            payment_id=None,
            error_message="Invalid amount"
        )
    
    # Simulate declined cards - cards starting with "0" are declined
    if card_number.startswith("0"):
        return PaymentResult(
            success=False,
            payment_id=None,
            error_message="Card declined by issuer"
        )
    
    # Generate a payment ID for successful transactions
    payment_id = f"pay_{uuid.uuid4().hex[:16]}"
    
    return PaymentResult(
        success=True,
        payment_id=payment_id,
        error_message=None
    )

