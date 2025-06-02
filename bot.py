import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import BOT_TOKEN
from routers.commands import router as commands_router
from routers.handlers.recipe_handlers import router as recipe_router
from middlewares.throttling import ThrottlingMiddleware
from utils.logger import setup_logger

async def main():
    # логер
    setup_logger()
    
    # бот и диспетчер
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # middleware
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    # роутеры
    dp.include_router(commands_router)
    dp.include_router(recipe_router)
    
    # удаляем старые апдейты и запускаем
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info("бот запущен")
    asyncio.run(main())