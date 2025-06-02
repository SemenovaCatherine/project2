import logging
import os
from config.settings import LOG_FILE

def setup_logger():
    # создаем папку для логов
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )