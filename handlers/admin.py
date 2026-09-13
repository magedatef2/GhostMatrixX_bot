"""
Owner-only commands.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config
from database.db import SessionLocal
from database.models import User, NumberOrder, Payment


def _is_owner(update: Update) -> bool:
    return update.effective_user.id == config.OWNER_ID


async def _deny(update: Update) -> None:
    if update.message:
        await update.message.reply_text("⛔ هذا الأمر للمالك فقط.")


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_owner(update):
        await _deny(update)
        return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 المستخدمون", callback_data="admin:users")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin:stats")],
        [InlineKeyboardButton("🎁 إعطاء رقم", callback_data="admin:give")],
    ])
    await update.message.reply_text("👑 *لوحة المالك*", parse_mode="Markdown", reply_markup=kb)


async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /give <telegram_id> <platform> <country> """
    if not _is_owner(update):
        await _deny(update)
        return
    args = context.args
    if len(args) != 3:
        await update.message.reply_text(
            "الاستخدام: `/give <telegram_id> <platform> <country>`\n"
            "مثال: `/give 123456789 whatsapp EG`",
            parse_mode="Markdown",
        )
        return
    target_id = int(args[0])
    platform, country = args[1], args[2]
    # TODO: purchase via sms_provider
    await update.message.reply_text(
        f"🎁 تم إصدار رقم مجاني للمستخدم `{target_id}`\n"
        f"المنصة: {platform} | الدولة: {country}",
        parse_mode="Markdown",
    )


async def myfree_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /myfree <platform> <country> """
    if not _is_owner(update):
        await _deny(update)
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "الاستخدام: `/myfree <platform> <country>`",
            parse_mode="Markdown",
        )
        return
    platform, country = args[0], args[1]
    await update.message.reply_text(
        f"👑 تم إصدار رقم خاص لك:\nالمنصة: {platform} | الدولة: {country}\n"
        f"المدة: {config.FREE_NUMBER_DURATION_HOURS} ساعة",
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_owner(update):
        await _deny(update)
        return
    session = SessionLocal()
    try:
        users = session.query(User).count()
        orders = session.query(NumberOrder).count()
        payments = session.query(Payment).count()
    finally:
        session.close()
    await update.message.reply_text(
        f"📊 *الإحصائيات*\n\n"
        f"👥 المستخدمون: {users}\n"
        f"📱 الأرقام: {orders}\n"
        f"💳 المدفوعات: {payments}",
        parse_mode="Markdown",
    )
