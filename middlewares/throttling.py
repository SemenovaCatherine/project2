import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_call = {}
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        
        # проверяем последний вызов
        if user_id in self.last_call:
            time_passed = current_time - self.last_call[user_id]
            if time_passed < self.rate_limit:
                if isinstance(event, Message):
                    await event.answer("⏳ слишком быстро! подождите секунду")
                return
        
        self.last_call[user_id] = current_time
        return await handler(event, data)