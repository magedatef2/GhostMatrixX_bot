"""
Database models for GhostMatrixX Bot.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    balance = Column(Integer, default=0)  # in EGP
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class NumberOrder(Base):
    __tablename__ = "number_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    platform = Column(String(32), nullable=False)   # whatsapp, telegram, ...
    country = Column(String(8), nullable=False)     # EG, US, ...
    phone_number = Column(String(32), nullable=False)
    provider = Column(String(32), nullable=False)   # virtualsms, mrxsim
    provider_order_id = Column(String(128), nullable=True)
    sms_code = Column(String(16), nullable=True)
    status = Column(String(16), default="pending")  # pending, active, expired, refunded
    is_free = Column(Boolean, default=False)
    price = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    method = Column(String(16), nullable=False)  # vodafone, orange, etisalat, we
    reference = Column(String(64), unique=True, nullable=False)
    status = Column(String(16), default="pending")  # pending, confirmed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
