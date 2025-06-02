import os
from dotenv import load_dotenv

load_dotenv()

# токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '7868985860:AAGwDeR9GK_wdDomnSV8UvpKWN5Pml83dVw')

# api настройки
MEAL_API_URL = 'https://www.themealdb.com/api/json/v1/1'
CACHE_TIME = 300  # 5 минут кэш

# файлы
DATA_FILE = 'storage/data.json'
LOG_FILE = 'logs/bot.log'