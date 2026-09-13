from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def button(text, callback):

    return InlineKeyboardButton(
        text=text,
        callback_data=callback,
    )


def markup(rows):

    return InlineKeyboardMarkup(rows)


# =========================================================
# MAIN
# =========================================================

def main_keyboard():

    return markup([

        [
            button("🌍 الدول", "countries"),
            button("📱 الأرقام", "numbers"),
        ],

        [
            button("🧾 طلباتي", "orders"),
            button("💬 الرسائل", "messages"),
        ],

        [
            button("📊 الإحصائيات", "stats"),
            button("👥 المستخدمون", "users"),
        ],

        [
            button("🛡 لوحة الإدارة", "admin"),
            button("⚙️ الإعدادات", "settings"),
        ],

        [
            button("ℹ️ معلومات", "info"),
        ],
    ])


# =========================================================
# ADMIN
# =========================================================

def admin_keyboard():

    return markup([

        [
            button("🌍 إدارة الدول", "admin:countries"),
            button("➕ إضافة دولة", "admin:add_country"),
        ],

        [
            button("📱 إدارة الأرقام", "admin:numbers"),
            button("➕ إضافة رقم", "admin:add_number"),
        ],

        [
            button("🔄 تدوير الأرقام", "admin:rotate"),
            button("🗑 حذف رقم", "admin:delete_number"),
        ],

        [
            button("🧾 إدارة الطلبات", "admin:orders"),
            button("📜 سجل العمليات", "admin:audit"),
        ],

        [
            button("📣 بث رسالة", "admin:broadcast"),
        ],

        [
            button("📊 إحصائيات متقدمة", "stats"),
        ],

        [
            button("⬅️ الرئيسية", "home"),
        ],
    ])


def back_home():

    return markup([
        [
            button("⬅️ الرئيسية", "home"),
        ]
    ])


# =========================================================
# COUNTRY LIST
# =========================================================

def country_keyboard(
    countries,
    prefix="country:",
):

    rows = []

    items = list(countries)

    for i in range(
        0,
        len(items),
        2,
    ):

        row = []

        for country in items[i:i + 2]:

            row.append(
                button(
                    country["name"],
                    f"{prefix}{country['id']}",
                )
            )

        rows.append(row)

    rows.append([
        button(
            "⬅️ الرئيسية",
            "home",
        )
    ])

    return markup(rows)


# =========================================================
# CONTINENTS
# =========================================================

def continent_keyboard():

    return markup([

        [
            button("🌍 أفريقيا", "continent:أفريقيا"),
            button("🌏 آسيا", "continent:آسيا"),
        ],

        [
            button("🇪🇺 أوروبا", "continent:أوروبا"),
            button(
                "🌎 أمريكا الشمالية",
                "continent:أمريكا الشمالية",
            ),
        ],

        [
            button(
                "🌎 أمريكا الجنوبية",
                "continent:أمريكا الجنوبية",
            ),
            button(
                "🌊 أوقيانوسيا",
                "continent:أوقيانوسيا",
            ),
        ],

        [
            button(
                "⬅️ الرئيسية",
                "home",
            )
        ],
    ])


# =========================================================
# NUMBER LIST
# =========================================================

def number_keyboard(
    numbers,
    back="countries",
):

    rows = []

    for number in numbers:

        rows.append([
            button(
                f"📱 {number['phone']}",
                f"take:{number['id']}",
            )
        ])

    rows.append([
        button(
            "⬅️ رجوع",
            back,
        )
    ])

    return markup(rows)


# =========================================================
# ADMIN NUMBER LIST
# =========================================================

def admin_number_keyboard(
    numbers,
):

    rows = []

    for number in numbers:

        text = (
            f"#{number['id']} "
            f"{number['phone']} "
            f"[{number['status']}]"
        )

        rows.append([
            button(
                text,
                f"manage_number:{number['id']}",
            )
        ])

    rows.append([
        button(
            "⬅️ الإدارة",
            "admin",
        )
    ])

    return markup(rows)


# =========================================================
# ADMIN COUNTRY LIST
# =========================================================

def admin_country_keyboard(
    countries,
):

    rows = []

    for country in countries:

        icon = (
            "🟢"
            if country["enabled"]
            else
            "🔴"
        )

        rows.append([
            button(
                f"{icon} {country['name']}",
                f"toggle_country:{country['id']}",
            )
        ])

    rows.append([
        button(
            "⬅️ الإدارة",
            "admin",
        )
    ])

    return markup(rows)


# =========================================================
# SETTINGS
# =========================================================

def settings_keyboard(
    maintenance,
    demo_otp,
):

    return markup([

        [
            button(
                "🔧 الصيانة: "
                + ("ON" if maintenance else "OFF"),
                "setting:maintenance",
            )
        ],

        [
            button(
                "🔐 OTP التجريبي: "
                + ("ON" if demo_otp else "OFF"),
                "setting:demo_otp",
            )
        ],

        [
            button(
                "⬅️ الرئيسية",
                "home",
            )
        ],
    ])
