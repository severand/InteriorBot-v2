# bot/main.py
# ✅ БЕЗ ЭМОДЗИ (Windows fix)

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from config import config, ADMIN_IDS
from database.db import db

from handlers import user_start, payment, admin
from handlers import creation
from handlers import design_step1_furniture
from handlers import design_step2_colors

# ===== ЛОГИРОВАНИЕ БЕЗ ЭМОДЗИ =====
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def handle_errors(update: Update, exception: Exception):
    """Обработчик всех ошибок"""
    logger.critical(f"ERROR: {type(exception).__name__}: {str(exception)}", exc_info=True)


async def main():
    """Главная функция"""

    logger.info("=" * 60)
    logger.info("BOT START")
    logger.info("=" * 60)

    try:
        logger.info("Initializing database...")
        await db.init_db()
        await db.init_analytics_table()
        logger.info("Database initialized")

        logger.info("Creating dispatcher...")
        dp = Dispatcher()
        logger.info("Dispatcher created")

        logger.info("Registering routers...")
        routers = [
            ("user_start", user_start.router),
            ("creation", creation.router),
            ("payment", payment.router),
            ("admin", admin.router),
            ("design_step1_furniture", design_step1_furniture.router),
            ("design_step2_colors", design_step2_colors.router),
        ]

        for name, router in routers:
            try:
                dp.include_router(router)
                logger.info(f"Router {name} registered")
            except Exception as e:
                logger.error(f"Error registering router {name}: {e}", exc_info=True)

        logger.info("All routers registered")

        logger.info("Setting context...")
        dp["admins"] = ADMIN_IDS
        dp["bot_token"] = config.BOT_TOKEN
        logger.info("Context set")

        logger.info("Registering error handler...")
        dp.errors.register(handle_errors)
        logger.info("Error handler registered")

        logger.info("Getting bot info...")
        me = await bot.get_me()
        logger.info(f"Bot: @{me.username} (ID: {me.id})")

        logger.info("=" * 60)
        logger.info("BOT READY TO WORK")
        logger.info("=" * 60)

        await dp.start_polling(bot)

    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

    finally:
        logger.info("Closing bot connection...")
        await bot.session.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("BOT STOPPED BY USER")
    except Exception as e:
        logger.critical(f"UNEXPECTED ERROR: {e}", exc_info=True)
