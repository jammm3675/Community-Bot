import asyncio
import logging
from loader import bot, dp
from handlers import router as main_router
from web_server import keep_alive


async def main():
    logging.basicConfig(level=logging.INFO)

    # Register routers
    dp.include_router(main_router)

    # Start web server
    keep_alive()

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
