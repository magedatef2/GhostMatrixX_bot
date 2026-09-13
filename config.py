import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

OWNER_ID_RAW = os.getenv("OWNER_ID", "0").strip()

DB_PATH = os.getenv("DB_PATH", "ghostnum.db").strip()

BOT_NAME = os.getenv("BOT_NAME", "GhostNum").strip()


try:
    OWNER_ID = int(OWNER_ID_RAW)
except ValueError:
    raise RuntimeError("OWNER_ID must be a valid Telegram numeric ID.")


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is missing.\n"
        "Create a .env file and add your new Telegram bot token."
    )


if OWNER_ID <= 0:
    raise RuntimeError(
        "OWNER_ID is invalid."
    )
