"""
GhostNum Demo Provider

هذه الطبقة مصممة لكي يكون من السهل لاحقًا
إضافة مزود أرقام حقيقي مرخص.

النسخة الحالية:
- لا تتصل بخدمات SMS حقيقية.
- لا تعترض OTP.
- لا تتصل بـ WhatsApp أو Telegram أو Facebook وغيرها.
- تولد أرقامًا تجريبية محلية.
- تولد OTP تجريبيًا محليًا.
"""

import random

import database as db


def seed_demo_numbers():

    countries = db.countries()

    for country in countries:

        # نضع رقمين تجريبيين لكل دولة.
        # هذه أرقام محلية غير مخصصة لخدمة خارجية.

        for index in range(1, 3):

            phone = (
                f"{country['dial_code']}"
                f"000000{index}"
            )

            try:

                db.add_number(
                    country["id"],
                    phone,
                    "temporary",
                )

            except Exception:

                # الرقم موجود بالفعل.
                pass


def generate_demo_otp():

    return f"{random.randint(0, 999999):06d}"


def create_demo_message(
    number_id,
):

    code = generate_demo_otp()

    db.add_message(
        number_id,
        f"DEMO OTP: {code}",
        "GhostNum Demo",
    )

    return code


class ProviderInterface:
    """
    واجهة عامة لأي مزود أرقام شرعي.
    """

    def list_numbers(self):
        raise NotImplementedError

    def reserve_number(self, number):
        raise NotImplementedError

    def release_number(self, number):
        raise NotImplementedError

    def get_messages(self, number):
        raise NotImplementedError


class DemoProvider(ProviderInterface):

    def list_numbers(self):

        return db.numbers(
            status="available"
        )

    def reserve_number(self, number):

        return True

    def release_number(self, number):

        return True

    def get_messages(self, number):

        return db.number_messages(
            number["id"]
        )


provider = DemoProvider()
