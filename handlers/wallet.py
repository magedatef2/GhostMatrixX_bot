"""
Wallet and manual payment flow.
"""
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config
from database.db import SessionLocal
from database.models import User, Payment


def wallet_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 شحن الرصيد", callback_data="wallet:topup")],
        [InlineKeyboardButton("🧾 آخر العمليات", callback_data="wallet:history")],
    ])


def method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 فودافون كاش", callback_data="wallet:method:vodafone")],
        [InlineKeyboardButton("🟠 أورنج موني", callback_data="wallet:method:orange")],
        [InlineKeyboardButton("🟢 اتصالات كاش", callback_data="wallet:method:etisalat")],
        [InlineKeyboardButton("🟣 WE Pay", callback_data="wallet:method:we")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="wallet:menu")],
    ])


async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show_wallet(update.effective_user.id, update.message.reply_text)


async def wallet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "wallet:menu":
        await _show_wallet(update.effective_user.id, query.edit_message_text)
        return

    if data == "wallet:topup":
        await query.edit_message_text(
            "💳 *اختر وسيلة الدفع:*",
            parse_mode="Markdown",
            reply_markup=method_keyboard(),
        )
        return

    if data == "wallet:history":
        await query.edit_message_text(
            "🧾 *آخر العمليات*\n\n_(سيتم تفعيلها مع تكامل الدفع)_",
            parse_mode="Markdown",
            reply_markup=wallet_keyboard(),
        )
        return

    if data.startswith("wallet:method:"):
        method = data.split(":")[2]
        ref = f"GMX-{uuid.uuid4().hex[:10].upper()}"
        session = SessionLocal()
        try:
            p = Payment(
                telegram_id=update.effective_user.id,
                amount=config.PRICE_PER_NUMBER,
                method=method,
                reference=ref,
                status="pending",
            )
            session.add(p)
            session.commit()
        finally:
            session.close()

        text = (
            f"💳 *تعليمات الدفع*\n\n"
            f"حوّل مبلغ *{config.PRICE_PER_NUMBER} جنيه* إلى:\n"
            f"`{config.PAYMOB_WALLET_NUMBER}`\n\n"
            f"المرجع: `{ref}`\n\n"
            f"بعد التحويل، أرسل صورة الإيصال للمالك {config.ADMIN_CONTACT}."
        )
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=wallet_keyboard(),
        )
        return


async def _show_wallet(telegram_id: int, sender) -> None:
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, balance=0)
            session.add(user)
            session.commit()
            balance = 0
        else:
            balance = user.balance
    finally:
        session.close()

    text = f"💰 *محفظتك*\n\nالرصيد الحالي: *{balance} جنيه*"
    await sender(text, parse_mode="Markdown", reply_markup=wallet_keyboard())
