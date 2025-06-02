from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

class FavoritesFilter(BaseFilter):
    """фильтр для колбэков избранного"""
    
    async def __call__(self, callback: CallbackQuery) -> bool:
        if not callback.data:
            return False
        
        return callback.data.startswith(('add_fav_', 'remove_fav_', 'show_fav_'))