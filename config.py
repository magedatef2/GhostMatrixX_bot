"""
GhostMatrixX Bot - Configuration Loader
Loads all environment variables safely.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///ghostmatrixx.db")

    # SMS Providers
    VIRTUALSMS_API_KEY: str = os.getenv("VIRTUALSMS_API_KEY", "")
    MRXSIM_API_KEY: str = os.getenv("MRXSIM_API_KEY", "")

    # Payment
    PAYMOB_API_KEY: str = os.getenv("PAYMOB_API_KEY", "")
    PAYMOB_INTEGRATION_ID: str = os.getenv("PAYMOB_INTEGRATION_ID", "")
    PAYMOB_HMAC_SECRET: str = os.getenv("PAYMOB_HMAC_SECRET", "")
    PAYMOB_WALLET_NUMBER: str = os.getenv("PAYMOB_WALLET_NUMBER", "01211853202")

    # Business
    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "EGP")
    FREE_NUMBER_DURATION_HOURS: int = int(os.getenv("FREE_NUMBER_DURATION_HOURS", "72"))
    ADMIN_CONTACT: str = os.getenv("ADMIN_CONTACT", "@owner")
    PRICE_PER_NUMBER: int = int(os.getenv("PRICE_PER_NUMBER", "50"))

    @classmethod
    def validate(cls) -> None:
        """Raise if critical settings are missing."""
        if not cls.BOT_TOKEN or ":" not in cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN غير صحيح أو مفقود في .env")
        if cls.OWNER_ID == 0:
            raise ValueError("OWNER_ID مفقود في .env")


config = Config()
