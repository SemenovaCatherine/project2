from aiogram.fsm.state import State, StatesGroup

class RecipeStates(StatesGroup):
    waiting_search = State()  # ожидание названия рецепта
    waiting_menu_day = State()  # ожидание дня для меню