"""
SMS provider integration (VirtualSMS / MRXSIM).
Starter template — fill API calls once you have provider accounts.
"""
from typing import Optional
import logging

from config import config

logger = logging.getLogger(__name__)


class SMSProviderError(Exception):
    pass


def buy_number(platform: str, country: str) -> dict:
    """
    Request a temporary number from the configured provider.
    Returns: {"phone_number": str, "order_id": str, "provider": str}
    """
    if config.VIRTUALSMS_API_KEY:
        return _buy_virtualsms(platform, country)
    if config.MRXSIM_API_KEY:
        return _buy_mrxsim(platform, country)
    raise SMSProviderError("لا يوجد مزود أرقام مُهيأ في .env")


def wait_for_sms(order_id: str) -> Optional[str]:
    """Poll provider until the OTP arrives. Returns code or None."""
    # TODO: implement per provider
    return None


def _buy_virtualsms(platform: str, country: str) -> dict:
    # TODO: real API call
    raise NotImplementedError("VirtualSMS integration pending")


def _buy_mrxsim(platform: str, country: str) -> dict:
    # TODO: real API call
    raise NotImplementedError("MRXSIM integration pending")
