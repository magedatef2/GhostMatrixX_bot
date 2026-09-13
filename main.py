"""
GhostMatrixX Bot - Entry Point
"""
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config import config
from database.db import init_db
from handlers import start, buy, my_numbers, wallet, admin

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("GhostMatrixX")


def main() -> None:
    config.validate()
    init_db()

    app = Application.builder().token(config.BOT_TOKEN).build()

    # Core
    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(CommandHandler("help", start.help_command))

    # Buy
    app.add_handler(CommandHandler("buy", buy.buy_command))
    app.add_handler(CallbackQueryHandler(buy.buy_callback, pattern=r"^buy:"))

    # My numbers
    app.add_handler(CommandHandler("mynumbers", my_numbers.my_numbers_command))
    app.add_handler(CallbackQueryHandler(my_numbers.my_numbers_callback, pattern=r"^mynum:"))

    # Wallet
    app.add_handler(CommandHandler("wallet", wallet.wallet_command))
    app.add_handler(CallbackQueryHandler(wallet.wallet_callback, pattern=r"^wallet:"))

    # Admin
    app.add_handler(CommandHandler("admin", admin.admin_command))
    app.add_handler(CommandHandler("give", admin.give_command))
    app.add_handler(CommandHandler("myfree", admin.myfree_command))
    app.add_handler(CommandHandler("stats", admin.stats_command))

    logger.info("👻 GhostMatrixX Bot starting...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
