"""
My numbers list.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.db import SessionLocal
from database.models import NumberOrder


async def my_numbers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_list(update.effective_user.id, update.message.reply_text)


async def my_numbers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "mynum:list":
        await _send_list(update.effective_user.id, query.edit_message_text)


async def _send_list(telegram_id: int, sender) -> None:
    session = SessionLocal()
    try:
        orders = (
            session.query(NumberOrder)
            .filter(NumberOrder.telegram_id == telegram_id)
            .order_by(NumberOrder.created_at.desc())
            .limit(20)
            .all()
        )
    finally:
        session.close()

    if not orders:
        await sender("📭 لا توجد أرقام لديك حالياً.")
        return

    lines = ["📋 *أرقامك الأخيرة:*\n"]
    for o in orders:
        lines.append(
            f"• `{o.phone_number}` — {o.platform.upper()} ({o.country})\n"
            f"  الحالة: {o.status} | كود: {o.sms_code or '—'}"
        )
    text = "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="buy:menu")]])
    await sender(text, parse_mode="Markdown", reply_markup=kb)
