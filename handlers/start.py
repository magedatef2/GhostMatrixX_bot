"""
/start and /help commands.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config


def main_menu(is_owner: bool) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📱 شراء رقم", callback_data="buy:menu")],
        [
            InlineKeyboardButton("📋 أرقامي", callback_data="mynum:list"),
            InlineKeyboardButton("💰 المحفظة", callback_data="wallet:menu"),
        ],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")],
    ]
    if is_owner:
        rows.append([InlineKeyboardButton("👑 لوحة المالك", callback_data="admin:panel")])
    return InlineKeyboardMarkup(rows)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    is_owner = user.id == config.OWNER_ID

    text = (
        f"👻 *أهلاً بك في GhostMatrixX*\n\n"
        f"مرحباً {user.mention_html()}\n"
        f"نظام احترافي للأرقام المؤقتة.\n\n"
        f"استخدم الأزرار بالأسفل للبدء."
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu(is_owner),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 *الأوامر المتاحة*\n\n"
        "/start - القائمة الرئيسية\n"
        "/buy - شراء رقم جديد\n"
        "/mynumbers - أرقامي\n"
        "/wallet - المحفظة\n"
        "/help - المساعدة\n\n"
        f"للدعم: {config.ADMIN_CONTACT}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
