import logging

from telegram import Update

from telegram.constants import ParseMode

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import database as db

from config import (
    BOT_NAME,
    BOT_TOKEN,
    OWNER_ID,
)

from countries import (
    COUNTRIES,
)

from provider import (
    create_demo_message,
    seed_demo_numbers,
)

from keyboards import (
    admin_country_keyboard,
    admin_keyboard,
    admin_number_keyboard,
    back_home,
    continent_keyboard,
    country_keyboard,
    main_keyboard,
    markup,
    button,
    number_keyboard,
    settings_keyboard,
)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    BOT_NAME
)


# =========================================================
# STATES
# =========================================================

STATE_ADD_COUNTRY = "add_country"

STATE_SELECT_NUMBER_COUNTRY = (
    "select_number_country"
)

STATE_ADD_NUMBER = "add_number"

STATE_BROADCAST = "broadcast"


# =========================================================
# SECURITY
# =========================================================

def is_owner(user):

    return bool(
        user
        and
        user.id == OWNER_ID
    )


async def reject_non_owner(update):

    if update.effective_message:

        await update.effective_message.reply_text(
            "⛔ هذا البوت خاص بالمالك."
        )


# =========================================================
# TEXT HELPERS
# =========================================================

def html_escape(value):

    if value is None:

        return ""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    if not is_owner(user):

        await reject_non_owner(update)

        return

    db.upsert_user(
        user.id,
        user.first_name or "",
        user.username or "",
    )

    welcome = db.get_setting(
        "welcome",
        "👻 أهلاً بك في GhostNum",
    )

    await update.effective_message.reply_text(
        f"{welcome}\n\n"
        f"🛡 <b>{BOT_NAME}</b>\n"
        "لوحة التحكم الرئيسية جاهزة.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


# =========================================================
# PANEL
# =========================================================

async def panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not is_owner(update.effective_user):

        await reject_non_owner(update)

        return

    await update.effective_message.reply_text(
        "🛡 <b>لوحة الإدارة</b>\n\n"
        "اختر العملية المطلوبة:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_keyboard(),
    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    if not is_owner(user):

        await query.edit_message_text(
            "⛔ غير مصرح."
        )

        return

    data = query.data


    # =====================================================
    # HOME
    # =====================================================

    if data == "home":

        await query.edit_message_text(
            f"👻 <b>{BOT_NAME}</b>\n\n"
            "اختر من القائمة:",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # COUNTRIES
    # =====================================================

    if data == "countries":

        await query.edit_message_text(
            "🌍 <b>اختر القارة</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=continent_keyboard(),
        )

        return


    # =====================================================
    # CONTINENT
    # =====================================================

    if data.startswith("continent:"):

        continent = data.split(
            ":",
            1,
        )[1]

        countries = db.countries(
            enabled_only=True,
            continent=continent,
        )

        await query.edit_message_text(
            f"🌍 <b>{html_escape(continent)}</b>\n\n"
            "اختر الدولة:",
            parse_mode=ParseMode.HTML,
            reply_markup=country_keyboard(
                countries
            ),
        )

        return


    # =====================================================
    # COUNTRY
    # =====================================================

    if data.startswith("country:"):

        country_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        country = db.country(
            country_id
        )

        if not country:

            await query.edit_message_text(
                "❌ الدولة غير موجودة.",
                reply_markup=back_home(),
            )

            return

        numbers = db.numbers(
            country_id=country_id,
            status="available",
            limit=50,
        )

        text = (
            f"🌍 <b>{html_escape(country['name'])}</b>\n\n"
            f"☎️ الكود: "
            f"<code>{country['dial_code']}</code>\n"
            f"🟢 المتاح: {len(numbers)}\n\n"
            "اختر رقمًا:"
        )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=number_keyboard(
                numbers
            ),
        )

        return


    # =====================================================
    # TAKE NUMBER
    # =====================================================

    if data.startswith("take:"):

        number_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        result = db.create_order(
            user.id,
            number_id,
        )

        if not result:

            await query.edit_message_text(
                "❌ الرقم لم يعد متاحًا.",
                reply_markup=main_keyboard(),
            )

            return

        order_id, number_row = result

        demo_enabled = (
            db.get_setting(
                "demo_otp",
                "1",
            )
            == "1"
        )

        if demo_enabled:

            code = create_demo_message(
                number_id
            )

            otp_text = (
                f"🔐 OTP تجريبي: "
                f"<code>{code}</code>"
            )

        else:

            otp_text = (
                "🔐 OTP التجريبي معطل."
            )

        db.audit(
            user.id,
            "create_order",
            f"order={order_id};number={number_id}",
        )

        await query.edit_message_text(
            "✅ <b>تم حجز الرقم</b>\n\n"
            f"📱 الرقم: "
            f"<code>{html_escape(number_row['phone'])}</code>\n"
            f"🧾 الطلب: #{order_id}\n\n"
            f"{otp_text}\n\n"
            "⚠️ الرقم وOTP في هذه النسخة "
            "تجريبيان ومحليان فقط.",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # NUMBERS
    # =====================================================

    if data == "numbers":

        numbers = db.numbers(
            limit=100,
        )

        if not numbers:

            text = "📱 لا توجد أرقام."

        else:

            lines = []

            for number in numbers:

                lines.append(
                    f"#{number['id']} "
                    f"{number['phone']} "
                    f"— {number['status']}"
                )

            text = (
                "📱 <b>الأرقام</b>\n\n"
                +
                "\n".join(lines)
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # USER ORDERS
    # =====================================================

    if data == "orders":

        orders = db.user_orders(
            user.id
        )

        if not orders:

            text = (
                "🧾 <b>طلباتي</b>\n\n"
                "لا توجد طلبات."
            )

        else:

            lines = []

            for order in orders:

                lines.append(
                    f"#{order['id']} | "
                    f"{order['phone'] or '-'} | "
                    f"{order['status']}"
                )

            text = (
                "🧾 <b>طلباتي</b>\n\n"
                +
                "\n".join(lines)
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # MESSAGES
    # =====================================================

    if data == "messages":

        orders = db.user_orders(
            user.id
        )

        messages = []

        for order in orders:

            number_id = order[
                "number_id"
            ]

            if not number_id:

                continue

            rows = db.number_messages(
                number_id,
                10,
            )

            for message in rows:

                messages.append(
                    f"📱 {order['phone']}\n"
                    f"💬 {message['body']}\n"
                    f"🕐 {message['created_at']}"
                )

        if messages:

            text = (
                "💬 <b>الرسائل</b>\n\n"
                +
                "\n\n".join(messages)
            )

        else:

            text = (
                "💬 <b>الرسائل</b>\n\n"
                "لا توجد رسائل."
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # STATS
    # =====================================================

    if data == "stats":

        stats = db.stats()

        text = (
            "📊 <b>إحصائيات GhostNum</b>\n\n"

            f"👥 المستخدمون: "
            f"{stats['users']}\n"

            f"🌍 الدول: "
            f"{stats['countries']}\n"

            f"🟢 الدول المفعلة: "
            f"{stats['enabled_countries']}\n\n"

            f"📱 إجمالي الأرقام: "
            f"{stats['numbers']}\n"

            f"🟢 الأرقام المتاحة: "
            f"{stats['available']}\n"

            f"🔴 الأرقام المستخدمة: "
            f"{stats['used']}\n\n"

            f"🧾 إجمالي الطلبات: "
            f"{stats['orders']}\n"

            f"⚡ الطلبات النشطة: "
            f"{stats['active_orders']}\n\n"

            f"💬 الرسائل: "
            f"{stats['messages']}"
        )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # USERS
    # =====================================================

    if data == "users":

        users = db.users(
            100
        )

        if not users:

            text = (
                "👥 لا يوجد مستخدمون."
            )

        else:

            lines = []

            for user_row in users:

                username = (
                    "@"
                    + user_row["username"]
                    if user_row["username"]
                    else "-"
                )

                lines.append(
                    f"👤 {user_row['user_id']} "
                    f"— {username}"
                )

            text = (
                "👥 <b>المستخدمون</b>\n\n"
                +
                "\n".join(lines)
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


    # =====================================================
    # ADMIN
    # =====================================================

    if data == "admin":

        await query.edit_message_text(
            "🛡 <b>لوحة الإدارة الكاملة</b>\n\n"
            "اختر العملية:",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # ADMIN COUNTRIES
    # =====================================================

    if data == "admin:countries":

        countries = db.countries()

        await query.edit_message_text(
            "🌍 <b>إدارة الدول</b>\n\n"
            "🟢 مفعلة\n"
            "🔴 معطلة\n\n"
            "اضغط على الدولة لتغيير حالتها.",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_country_keyboard(
                countries
            ),
        )

        return


    # =====================================================
    # TOGGLE COUNTRY
    # =====================================================

    if data.startswith(
        "toggle_country:"
    ):

        country_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        db.toggle_country(
            country_id
        )

        db.audit(
            user.id,
            "toggle_country",
            str(country_id),
        )

        await query.edit_message_text(
            "✅ تم تغيير حالة الدولة.",
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # ADD COUNTRY
    # =====================================================

    if data == "admin:add_country":

        context.user_data[
            "state"
        ] = STATE_ADD_COUNTRY

        await query.edit_message_text(
            "➕ <b>إضافة دولة</b>\n\n"
            "أرسل البيانات بهذا الشكل:\n\n"
            "<code>🇺🇸 أمريكا | +1 | أمريكا الشمالية</code>\n\n"
            "الترتيب:\n"
            "اسم الدولة | كود الاتصال | القارة",
            parse_mode=ParseMode.HTML,
        )

        return


    # =====================================================
    # ADMIN NUMBERS
    # =====================================================

    if data == "admin:numbers":

        numbers = db.numbers(
            limit=100
        )

        await query.edit_message_text(
            "📱 <b>إدارة الأرقام</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_number_keyboard(
                numbers
            ),
        )

        return


    # =====================================================
    # ADD NUMBER
    # =====================================================

    if data == "admin:add_number":

        context.user_data[
            "state"
        ] = STATE_SELECT_NUMBER_COUNTRY

        countries = db.countries(
            enabled_only=True
        )

        await query.edit_message_text(
            "➕ <b>إضافة رقم</b>\n\n"
            "اختر الدولة:",
            parse_mode=ParseMode.HTML,
            reply_markup=country_keyboard(
                countries,
                prefix="new_number_country:",
            ),
        )

        return


    # =====================================================
    # SELECT NUMBER COUNTRY
    # =====================================================

    if data.startswith(
        "new_number_country:"
    ):

        country_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        context.user_data[
            "new_number_country"
        ] = country_id

        context.user_data[
            "state"
        ] = STATE_ADD_NUMBER

        await query.edit_message_text(
            "📱 <b>إضافة رقم</b>\n\n"
            "أرسل الرقم والنوع:\n\n"
            "<code>+201000000000 | temporary</code>\n\n"
            "الأنواع:\n"
            "temporary\n"
            "permanent",
            parse_mode=ParseMode.HTML,
        )

        return


    # =====================================================
    # MANAGE NUMBERS
    # =====================================================

    if data.startswith(
        "manage_number:"
    ):

        number_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        number = db.number(
            number_id
        )

        if not number:

            await query.edit_message_text(
                "❌ الرقم غير موجود.",
                reply_markup=admin_keyboard(),
            )

            return

        text = (
            "📱 <b>تفاصيل الرقم</b>\n\n"

            f"ID: <code>{number['id']}</code>\n"
            f"الرقم: <code>{html_escape(number['phone'])}</code>\n"
            f"الدولة: {html_escape(number['country_name'])}\n"
            f"القارة: {html_escape(number['continent'])}\n"
            f"النوع: {number['kind']}\n"
            f"الحالة: {number['status']}"
        )

        keyboard = markup([

            [
                button(
                    "🔄 تدوير",
                    f"rotate:{number_id}",
                ),

                button(
                    "🗑 حذف",
                    f"delete_number:{number_id}",
                ),
            ],

            [
                button(
                    "💬 الرسائل",
                    f"number_messages:{number_id}",
                )
            ],

            [
                button(
                    "⬅️ الإدارة",
                    "admin",
                )
            ],
        ])

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )

        return


    # =====================================================
    # ROTATE
    # =====================================================

    if data == "admin:rotate":

        numbers = db.numbers(
            status="used",
            limit=100,
        )

        rows = []

        for number in numbers:

            rows.append([
                button(
                    f"🔄 {number['phone']}",
                    f"rotate:{number['id']}",
                )
            ])

        rows.append([
            button(
                "⬅️ الإدارة",
                "admin",
            )
        ])

        await query.edit_message_text(
            "🔄 <b>تدوير الأرقام المستخدمة</b>\n\n"
            "اختر الرقم لإعادته إلى المخزون:",
            parse_mode=ParseMode.HTML,
            reply_markup=markup(rows),
        )

        return


    # =====================================================
    # ROTATE NUMBER
    # =====================================================

    if data.startswith(
        "rotate:"
    ):

        number_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        result = db.rotate_number(
            number_id
        )

        if result:

            db.audit(
                user.id,
                "rotate_number",
                str(number_id),
            )

            text = (
                "🔄 <b>تم تدوير الرقم</b>\n\n"
                f"📱 {html_escape(result['phone'])}\n\n"
                "الحالة أصبحت: 🟢 available"
            )

        else:

            text = (
                "❌ الرقم غير موجود."
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # DELETE NUMBER MENU
    # =====================================================

    if data == "admin:delete_number":

        numbers = db.numbers(
            limit=100,
        )

        rows = []

        for number in numbers:

            rows.append([
                button(
                    f"🗑 {number['phone']}",
                    f"delete_number:{number['id']}",
                )
            ])

        rows.append([
            button(
                "⬅️ الإدارة",
                "admin",
            )
        ])

        await query.edit_message_text(
            "🗑 <b>حذف رقم</b>\n\n"
            "اختر الرقم:",
            parse_mode=ParseMode.HTML,
            reply_markup=markup(rows),
        )

        return


    # =====================================================
    # DELETE NUMBER
    # =====================================================

    if data.startswith(
        "delete_number:"
    ):

        number_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        number = db.number(
            number_id
        )

        if not number:

            await query.edit_message_text(
                "❌ الرقم غير موجود.",
                reply_markup=admin_keyboard(),
            )

            return

        db.delete_number(
            number_id
        )

        db.audit(
            user.id,
            "delete_number",
            number["phone"],
        )

        await query.edit_message_text(
            "🗑 <b>تم حذف الرقم</b>\n\n"
            f"<code>{html_escape(number['phone'])}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # NUMBER MESSAGES
    # =====================================================

    if data.startswith(
        "number_messages:"
    ):

        number_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        number = db.number(
            number_id
        )

        messages = db.number_messages(
            number_id,
            30,
        )

        lines = []

        for message in messages:

            lines.append(
                f"🕐 {message['created_at']}\n"
                f"👤 {message['sender']}\n"
                f"💬 {message['body']}"
            )

        text = (
            f"💬 <b>رسائل {html_escape(number['phone'])}</b>\n\n"
            +
            (
                "\n\n".join(lines)
                if lines
                else
                "لا توجد رسائل."
            )
        )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # ADMIN ORDERS
    # =====================================================

    if data == "admin:orders":

        orders = db.all_orders(
            100
        )

        rows = []

        for order in orders:

            rows.append([
                button(
                    f"#{order['id']} "
                    f"{order['phone'] or '-'} "
                    f"[{order['status']}]",
                    f"admin_order:{order['id']}",
                )
            ])

        rows.append([
            button(
                "⬅️ الإدارة",
                "admin",
            )
        ])

        await query.edit_message_text(
            "🧾 <b>إدارة الطلبات</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=markup(rows),
        )

        return


    # =====================================================
    # ADMIN ORDER DETAILS
    # =====================================================

    if data.startswith(
        "admin_order:"
    ):

        order_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        orders = db.all_orders(
            500
        )

        order = None

        for item in orders:

            if item["id"] == order_id:

                order = item

                break

        if not order:

            await query.edit_message_text(
                "❌ الطلب غير موجود.",
                reply_markup=admin_keyboard(),
            )

            return

        text = (
            "🧾 <b>تفاصيل الطلب</b>\n\n"

            f"ID: #{order['id']}\n"
            f"User: <code>{order['user_id']}</code>\n"
            f"الرقم: <code>{html_escape(order['phone'] or '-')}</code>\n"
            f"الدولة: {html_escape(order['country_name'] or '-')} \n"
            f"النوع: {order['kind'] or '-'}\n"
            f"الحالة: {order['status']}\n"
            f"التاريخ: {order['created_at']}"
        )

        keyboard_rows = []

        if order["status"] == "active":

            keyboard_rows.append([
                button(
                    "✅ إغلاق الطلب وإرجاع الرقم",
                    f"close_order:{order_id}",
                )
            ])

        keyboard_rows.append([
            button(
                "⬅️ الطلبات",
                "admin:orders",
            )
        ])

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=markup(
                keyboard_rows
            ),
        )

        return


    # =====================================================
    # CLOSE ORDER
    # =====================================================

    if data.startswith(
        "close_order:"
    ):

        order_id = int(
            data.split(
                ":",
                1,
            )[1]
        )

        result = db.close_order(
            order_id
        )

        if result:

            db.audit(
                user.id,
                "close_order",
                str(order_id),
            )

            text = (
                "✅ <b>تم إغلاق الطلب</b>\n\n"
                "وتم إعادة الرقم إلى المخزون."
            )

        else:

            text = (
                "❌ الطلب غير موجود."
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # AUDIT
    # =====================================================

    if data == "admin:audit":

        logs = db.audit_logs(
            50
        )

        lines = []

        for item in logs:

            lines.append(
                f"#{item['id']} "
                f"{item['action']} "
                f"— {item['details'] or '-'}\n"
                f"👤 {item['actor_id']} "
                f"🕐 {item['created_at']}"
            )

        text = (
            "📜 <b>سجل العمليات</b>\n\n"
            +
            (
                "\n\n".join(lines)
                if lines
                else
                "السجل فارغ."
            )
        )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


    # =====================================================
    # SETTINGS
    # =====================================================

    if data == "settings":

        maintenance = (
            db.get_setting(
                "maintenance",
                "0",
            )
            == "1"
        )

        demo_otp = (
            db.get_setting(
                "demo_otp",
                "1",
            )
            == "1"
        )

        await query.edit_message_text(
            "⚙️ <b>إعدادات البوت</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=settings_keyboard(
                maintenance,
                demo_otp,
            ),
        )

        return


    # =====================================================
    # SETTING TOGGLE
    # =====================================================

    if data.startswith(
        "setting:"
    ):

        key = data.split(
            ":",
            1,
        )[1]

        current = (
            db.get_setting(
                key,
                "0",
            )
            == "1"
        )

        new_value = (
            "0"
            if current
            else
            "1"
        )

        db.set_setting(
            key,
            new_value,
        )

        db.audit(
            user.id,
            "setting",
            f"{key}={new_value}",
        )

        maintenance = (
            db.get_setting(
                "maintenance",
                "0",
            )
            == "1"
        )

        demo_otp = (
            db.get_setting(
                "demo_otp",
                "1",
            )
            == "1"
        )

        await query.edit_message_text(
            "⚙️ <b>تم تحديث الإعداد</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=settings_keyboard(
                maintenance,
                demo_otp,
            ),
        )

        return


    # =====================================================
    # BROADCAST
    # =====================================================

    if data == "admin:broadcast":

        context.user_data[
            "state"
        ] = STATE_BROADCAST

        await query.edit_message_text(
            "📣 <b>Broadcast</b>\n\n"
            "أرسل الآن نص الرسالة.\n"
            "سيتم إرسالها إلى المستخدمين المسجلين.",
            parse_mode=ParseMode.HTML,
        )

        return


    # =====================================================
    # INFO
    # =====================================================

    if data == "info":

        await query.edit_message_text(
            f"ℹ️ <b>{BOT_NAME}</b>\n\n"
            "نظام إدارة واختبار محلي.\n\n"
            "المميزات:\n"
            "• إدارة الدول\n"
            "• إدارة الأرقام\n"
            "• الطلبات\n"
            "• تدوير الأرقام\n"
            "• الإحصائيات\n"
            "• المستخدمون\n"
            "• الإعدادات\n"
            "• سجل العمليات\n"
            "• Broadcast\n\n"
            "الأرقام وOTP التجريبية محلية فقط.",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(),
        )

        return


# =========================================================
# TEXT HANDLER
# =========================================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    if not is_owner(user):

        return

    state = context.user_data.get(
        "state"
    )

    text = (
        update.message.text or ""
    ).strip()


    # =====================================================
    # ADD COUNTRY
    # =====================================================

    if state == STATE_ADD_COUNTRY:

        try:

            name, code, continent = (
                part.strip()
                for part in text.split(
                    "|",
                    2,
                )
            )

            if not name:

                raise ValueError

            if not code.startswith(
                "+"
            ):

                raise ValueError

            db.add_country(
                name,
                code,
                continent,
            )

            db.audit(
                user.id,
                "add_country",
                name,
            )

            context.user_data.pop(
                "state",
                None,
            )

            await update.message.reply_text(
                "✅ <b>تمت إضافة الدولة.</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=admin_keyboard(),
            )

        except Exception:

            await update.message.reply_text(
                "❌ الصيغة غير صحيحة.\n\n"
                "استخدم:\n"
                "<code>🇺🇸 أمريكا | +1 | أمريكا الشمالية</code>",
                parse_mode=ParseMode.HTML,
            )

        return


    # =====================================================
    # ADD NUMBER
    # =====================================================

    if state == STATE_ADD_NUMBER:

        country_id = context.user_data.get(
            "new_number_country"
        )

        if not country_id:

            await update.message.reply_text(
                "❌ لم يتم اختيار الدولة."
            )

            return

        try:

            phone, kind = (
                part.strip()
                for part in text.split(
                    "|",
                    1,
                )
            )

            if kind not in (
                "temporary",
                "permanent",
            ):

                kind = "temporary"

            db.add_number(
                country_id,
                phone,
                kind,
            )

            db.audit(
                user.id,
                "add_number",
                phone,
            )

            context.user_data.clear()

            await update.message.reply_text(
                "✅ <b>تمت إضافة الرقم.</b>\n\n"
                f"📱 <code>{html_escape(phone)}</code>\n"
                f"النوع: {kind}",
                parse_mode=ParseMode.HTML,
                reply_markup=admin_keyboard(),
            )

        except Exception:

            await update.message.reply_text(
                "❌ تعذر إضافة الرقم.\n\n"
                "مثال:\n"
                "<code>+201000000000 | temporary</code>",
                parse_mode=ParseMode.HTML,
            )

        return


    # =====================================================
    # BROADCAST
    # =====================================================

    if state == STATE_BROADCAST:

        context.user_data.clear()

        all_users = db.users(
            10000
        )

        sent = 0

        failed = 0

        for user_row in all_users:

            try:

                await context.bot.send_message(
                    chat_id=user_row["user_id"],
                    text=text,
                )

                sent += 1

            except Exception:

                failed += 1

        db.audit(
            user.id,
            "broadcast",
            f"sent={sent};failed={failed}",
        )

        await update.message.reply_text(
            "📣 <b>انتهى البث</b>\n\n"
            f"✅ تم الإرسال: {sent}\n"
            f"❌ فشل: {failed}",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard(),
        )

        return


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update,
    context,
):

    logger.exception(
        "Unhandled exception",
        exc_info=context.error,
    )


# =========================================================
# MAIN
# =========================================================

def main():

    # إنشاء قاعدة البيانات
    db.init_db()

    # إضافة الدول الافتراضية
    db.seed_countries(
        COUNTRIES
    )

    # إنشاء المخزون التجريبي
    seed_demo_numbers()

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "panel",
            panel,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            callback
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_handler,
        )
    )

    application.add_error_handler(
        error_handler
    )

    logger.info(
        "%s started successfully.",
        BOT_NAME,
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":

    main()
