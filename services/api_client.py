import aiohttp
import asyncio
import time
import logging
from typing import Optional, Dict, List
from config.settings import MEAL_API_URL, CACHE_TIME

logger = logging.getLogger(__name__)

# простой кэш в памяти
cache = {}

class MealAPI:
    def __init__(self):
        self.base_url = MEAL_API_URL
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def _make_request(self, endpoint: str) -> Optional[Dict]:
        """делает запрос к api с обработкой ошибок"""
        url = f"{self.base_url}/{endpoint}"
        
        # проверяем кэш
        cache_key = url
        if cache_key in cache:
            cached_data, timestamp = cache[cache_key]
            if time.time() - timestamp < CACHE_TIME:
                logger.info(f"используем кэш для {url}")
                return cached_data
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # сохраняем в кэш
                        cache[cache_key] = (data, time.time())
                        logger.info(f"успешный запрос к {url}")
                        return data
                    else:
                        logger.error(f"ошибка api: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"таймаут при запросе к {url}")
            return None
        except Exception as e:
            logger.error(f"ошибка при запросе к api: {e}")
            return None
    
    async def search_by_name(self, name: str) -> List[Dict]:
        """ищет рецепты по названию"""
        if not name or len(name.strip()) < 2:
            return []
        
        endpoint = f"search.php?s={name}"
        data = await self._make_request(endpoint)
        
        if data and data.get('meals'):
            return data['meals']
        return []
    
    async def get_random_meal(self) -> Optional[Dict]:
        """получает случайный рецепт"""
        endpoint = "random.php"
        data = await self._make_request(endpoint)
        
        if data and data.get('meals'):
            return data['meals'][0]
        return None
    
    async def get_by_category(self, category: str) -> List[Dict]:
        """получает рецепты по категории"""
        endpoint = f"filter.php?c={category}"
        data = await self._make_request(endpoint)
        
        if data and data.get('meals'):
            return data['meals'][:5]  # только первые 5
        return []

    async def get_by_id(self, meal_id: str) -> Optional[Dict]:
        """получает рецепт по ID"""
        endpoint = f"lookup.php?i={meal_id}"
        data = await self._make_request(endpoint)
        
        if data and data.get('meals'):
            return data['meals'][0]
        return None

# singleton
meal_api = MealAPI()