"""
Buy number flow.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config

PLATFORMS = {
    "whatsapp": "واتساب",
    "telegram": "تيليجرام",
    "facebook": "فيسبوك",
    "instagram": "إنستجرام",
    "snapchat": "سناب شات",
    "tiktok": "تيك توك",
    "viber": "فايبر",
    "twitter": "تويتر",
}

COUNTRIES = {
    "EG": "🇪🇬 مصر",
    "US": "🇺🇸 أمريكا",
    "GB": "🇬🇧 بريطانيا",
    "DE": "🇩🇪 ألمانيا",
    "IN": "🇮🇳 الهند",
    "ID": "🇮🇩 إندونيسيا",
}


def platform_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"buy:platform:{code}")]
        for code, name in PLATFORMS.items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="buy:back")])
    return InlineKeyboardMarkup(buttons)


def country_keyboard(platform: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"buy:country:{platform}:{code}")]
        for code, name in COUNTRIES.items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="buy:menu")])
    return InlineKeyboardMarkup(buttons)


async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📱 *اختر المنصة:*",
        parse_mode="Markdown",
        reply_markup=platform_keyboard(),
    )


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "buy:menu":
        await query.edit_message_text(
            "📱 *اختر المنصة:*",
            parse_mode="Markdown",
            reply_markup=platform_keyboard(),
        )
        return

    if data == "buy:back":
        await query.edit_message_text(
            "👻 القائمة الرئيسية",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ رجوع", callback_data="buy:menu")]]
            ),
        )
        return

    parts = data.split(":")
    if len(parts) == 3 and parts[1] == "platform":
        platform = parts[2]
        await query.edit_message_text(
            f"🌍 *اختر الدولة لـ {PLATFORMS.get(platform, platform)}:*",
            parse_mode="Markdown",
            reply_markup=country_keyboard(platform),
        )
        return

    if len(parts) == 4 and parts[1] == "country":
        platform, country = parts[2], parts[3]
        price = config.PRICE_PER_NUMBER
        text = (
            f"🧾 *تأكيد الطلب*\n\n"
            f"المنصة: {PLATFORMS.get(platform, platform)}\n"
            f"الدولة: {COUNTRIES.get(country, country)}\n"
            f"السعر: {price} جنيه\n\n"
            f"هل تريد المتابعة؟"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد", callback_data=f"buy:confirm:{platform}:{country}")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="buy:menu")],
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return

    if len(parts) == 4 and parts[1] == "confirm":
        platform, country = parts[2], parts[3]
        # TODO: integrate with sms_provider to purchase a real number
        await query.edit_message_text(
            "⏳ جاري تجهيز الرقم...\n\n"
            "_(سيتم ربط مزود الأرقام في الخطوة التالية)_",
            parse_mode="Markdown",
        )
        return
