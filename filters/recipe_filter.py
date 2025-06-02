from aiogram.filters import BaseFilter
from aiogram.types import Message

class RecipeSearchFilter(BaseFilter):
    """фильтр для поиска рецептов - проверяет что сообщение не команда"""
    
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        
        # не команда и не пустое, минимум 3 символа
        text = message.text.strip()
        return not text.startswith('/') and len(text) >= 3 and len(text) <= 50