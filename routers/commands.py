import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_main_menu, get_categories_menu
from services.api_client import meal_api
from storage.data_manager import add_user, get_favorites, get_menu
from utils.formatters import format_recipe, format_favorites_list
from states.recipe_states import RecipeStates

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    """команда старт"""
    logger.info(f"пользователь {message.from_user.id} запустил бота")
    
    # добавляем пользователя
    await add_user(message.from_user.id, message.from_user.username)
    
    text = f"👋 привет, {message.from_user.first_name}!\n\n"
    text += "🍽 я твой кулинарный помощник!\n"
    text += "помогу найти рецепты, сохранить избранное и спланировать меню\n\n"
    text += "выбери что хочешь сделать:"
    
    await message.answer(text, reply_markup=get_main_menu())

@router.message(Command('help'))
async def cmd_help(message: Message):
    """команда помощь"""
    text = "🆘 <b>помощь по боту:</b>\n\n"
    text += "/start - запуск бота\n"
    text += "/help - эта справка\n"
    text += "/search - поиск рецептов\n"
    text += "/favorites - избранные рецепты\n"
    text += "/menu - меню на неделю\n\n"
    text += "🔍 <b>поиск:</b> просто напиши название блюда\n"
    text += "⭐ <b>избранное:</b> сохраняй понравившиеся рецепты\n"
    text += "📅 <b>меню:</b> планируй питание на неделю"
    
    await message.answer(text, reply_markup=get_main_menu())

@router.message(Command('search'))
async def cmd_search(message: Message, state: FSMContext):
    """команда поиск"""
    await state.set_state(RecipeStates.waiting_search)
    text = "🔍 напиши название блюда для поиска:\n\n"
    text += "💡 <b>подсказка:</b> лучше искать на английском\n"
    text += "например: pasta, pizza, chicken, beef, fish, cake\n"
    text += "или популярные блюда: carbonara, lasagna, risotto"
    await message.answer(text)

@router.message(Command('favorites'))
async def cmd_favorites(message: Message):
    """команда избранное"""
    favorites = await get_favorites(message.from_user.id)
    
    if not favorites:
        text = "🤷‍♀️ у вас пока нет избранных рецептов\n\nнайдите рецепт и добавьте его в избранное!"
        await message.answer(text, reply_markup=get_main_menu())
    else:
        text = "⭐ <b>ваши избранные рецепты:</b>\n\n"
        text += "выберите рецепт для просмотра:"
        from keyboards.inline import get_favorites_menu
        kb = get_favorites_menu(favorites)
        await message.answer(text, reply_markup=kb)

@router.message(Command('menu'))
async def cmd_menu(message: Message):
    """команда меню"""
    menu = await get_menu(message.from_user.id)
    
    if not menu:
        text = "📅 <b>ваше меню пусто</b>\n\n"
        text += "добавьте рецепты через поиск!"
    else:
        text = "📅 <b>ваше меню на неделю:</b>\n\n"
        days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        
        for day in days:
            if day in menu:
                recipe = menu[day]
                text += f"🗓 {day}: {recipe['name']}\n"
            else:
                text += f"🗓 {day}: не запланировано\n"
    
    await message.answer(text, reply_markup=get_main_menu())

# колбэки главного меню
@router.callback_query(F.data == "search_recipes")
async def cb_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RecipeStates.waiting_search)
    text = "🔍 напиши название блюда для поиска:\n\n"
    text += "💡 <b>подсказка:</b> лучше искать на английском\n"
    text += "например: pasta, pizza, chicken, beef, fish, cake"
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "random_recipe")
async def cb_random(callback: CallbackQuery):
    await callback.message.edit_text("🎲 ищу случайный рецепт...")
    
    recipe = await meal_api.get_random_meal()
    if recipe:
        text = format_recipe(recipe)
        from keyboards.inline import get_recipe_actions
        from storage.data_manager import is_favorite
        
        # сохраняем рецепт для пользователя
        user_id = callback.from_user.id
        from routers.handlers.recipe_handlers import user_recipes
        user_recipes[user_id] = recipe
        
        is_fav = await is_favorite(user_id, recipe['idMeal'])
        kb = get_recipe_actions(recipe['idMeal'], is_fav)
        
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text("😔 не удалось найти рецепт", reply_markup=get_main_menu())
    
    await callback.answer()

@router.callback_query(F.data == "show_favorites")
async def cb_favorites(callback: CallbackQuery):
    favorites = await get_favorites(callback.from_user.id)
    
    if not favorites:
        text = "🤷‍♀️ у вас пока нет избранных рецептов\n\nнайдите рецепт и добавьте его в избранное!"
        await callback.message.edit_text(text, reply_markup=get_main_menu())
    else:
        text = "⭐ <b>ваши избранные рецепты:</b>\n\n"
        text += "выберите рецепт для просмотра:"
        from keyboards.inline import get_favorites_menu
        kb = get_favorites_menu(favorites)
        await callback.message.edit_text(text, reply_markup=kb)
    
    await callback.answer()

@router.callback_query(F.data == "weekly_menu")
async def cb_menu(callback: CallbackQuery):
    menu = await get_menu(callback.from_user.id)
    
    if not menu:
        text = "📅 <b>ваше меню пусто</b>\n\nдобавьте рецепты через поиск!"
    else:
        text = "📅 <b>ваше меню:</b>\n\n"
        days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        for day in days:
            if day in menu:
                recipe = menu[day]
                text += f"🗓 {day}: {recipe['name']}\n"
            else:
                text += f"🗓 {day}: не запланировано\n"
    
    await callback.message.edit_text(text, reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def cb_back(callback: CallbackQuery):
    text = "🍽 <b>главное меню</b>\n\nвыбери действие:"
    await callback.message.edit_text(text, reply_markup=get_main_menu())
    await callback.answer()

# добавляем обработчик для возврата к избранному
@router.callback_query(F.data == "show_favorites")
async def go_to_favorites(callback: CallbackQuery):
    """переход к избранному"""
    favorites = await get_favorites(callback.from_user.id)
    
    if not favorites:
        text = "🤷‍♀️ у вас пока нет избранных рецептов\n\nнайдите рецепт и добавьте его в избранное!"
        await callback.message.edit_text(text, reply_markup=get_main_menu())
    else:
        text = "⭐ <b>ваши избранные рецепты:</b>\n\n"
        text += "выберите рецепт для просмотра:"
        from keyboards.inline import get_favorites_menu
        kb = get_favorites_menu(favorites)
        await callback.message.edit_text(text, reply_markup=kb)
    
    await callback.answer()