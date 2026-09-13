"""
Payment gateway integration (Paymob).
Starter template — fill API calls after merchant approval.
"""
import logging
from config import config

logger = logging.getLogger(__name__)


def create_payment_link(amount: int, reference: str, telegram_id: int) -> str:
    """
    Creates a Paymob payment link for the given amount.
    Returns the checkout URL.
    """
    # TODO: implement after Paymob merchant approval
    raise NotImplementedError("Paymob integration pending")


def verify_hmac(payload: dict, received_hmac: str) -> bool:
    """Verify Paymob webhook HMAC."""
    # TODO: implement HMAC verification
    return False
