import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from filters.recipe_filter import RecipeSearchFilter
from filters.favorites_filter import FavoritesFilter
from services.api_client import meal_api
from storage.data_manager import add_favorite, remove_favorite, is_favorite, save_menu
from utils.formatters import format_recipe
from keyboards.inline import get_recipe_actions, get_main_menu
from states.recipe_states import RecipeStates

logger = logging.getLogger(__name__)
router = Router()

# глобальное хранилище рецептов для пользователей
user_recipes = {}

@router.message(RecipeStates.waiting_search, RecipeSearchFilter())
async def search_recipe(message: Message, state: FSMContext):
    """поиск рецепта по названию"""
    query = message.text.strip()
    logger.info(f"поиск рецепта: {query}")
    
    await message.answer("🔍 ищу рецепты...")
    
    recipes = await meal_api.search_by_name(query)
    
    if recipes:
        # берем первый найденный
        recipe = recipes[0]
        text = format_recipe(recipe)
        
        # сохраняем рецепт для пользователя
        user_id = message.from_user.id
        user_recipes[user_id] = recipe
        
        is_fav = await is_favorite(user_id, recipe['idMeal'])
        kb = get_recipe_actions(recipe['idMeal'], is_fav)
        
        await message.answer(text, reply_markup=kb)
    else:
        await message.answer(
            f"😔 не найдено рецептов по запросу '{query}'\n\nпопробуй другое название",
            reply_markup=get_main_menu()
        )
    
    await state.clear()

@router.message(RecipeStates.waiting_search)
async def invalid_search(message: Message):
    """неверный ввод при поиске"""
    await message.answer("❌ введи корректное название блюда (минимум 2 символа)")

@router.callback_query(F.data.startswith("show_fav_"))
async def show_favorite_recipe(callback: CallbackQuery):
    """показать избранный рецепт"""
    recipe_id = callback.data.replace("show_fav_", "")
    logger.info(f"показ избранного рецепта {recipe_id} для пользователя {callback.from_user.id}")
    
    await callback.message.edit_text("🔍 загружаю рецепт...")
    
    # получаем рецепт из избранного
    from storage.data_manager import get_favorite_by_id
    recipe = await get_favorite_by_id(callback.from_user.id, recipe_id)
    
    if recipe:
        text = format_recipe(recipe)
        
        # сохраняем рецепт для пользователя
        user_id = callback.from_user.id
        user_recipes[user_id] = recipe
        
        # это точно избранный рецепт, показываем кнопку возврата к избранному
        kb = get_recipe_actions(recipe_id, True, from_favorites=True)
        
        await callback.message.edit_text(text, reply_markup=kb)
        logger.info(f"рецепт {recipe_id} успешно показан")
    else:
        await callback.message.edit_text(
            "😔 рецепт не найден в избранном",
            reply_markup=get_main_menu()
        )
        logger.error(f"рецепт {recipe_id} не найден в избранном")
    
    await callback.answer()

@router.callback_query(FavoritesFilter())
async def handle_favorites(callback: CallbackQuery):
    """обработка действий с избранным"""
    data = callback.data
    user_id = callback.from_user.id
    
    # получаем текущий рецепт пользователя
    recipe = user_recipes.get(user_id)
    
    if not recipe:
        await callback.answer("❌ рецепт не найден")
        return
    
    recipe_id = recipe['idMeal']
    
    if data.startswith("add_fav_"):
        success = await add_favorite(user_id, recipe)
        if success:
            await callback.answer("⭐ добавлено в избранное!")
            # обновляем кнопки
            kb = get_recipe_actions(recipe_id, True)
            await callback.message.edit_reply_markup(reply_markup=kb)
        else:
            await callback.answer("⚠️ уже в избранном!")
    
    elif data.startswith("remove_fav_"):
        success = await remove_favorite(user_id, recipe_id)
        if success:
            await callback.answer("❌ удалено из избранного")
            # обновляем кнопки
            kb = get_recipe_actions(recipe_id, False)
            await callback.message.edit_reply_markup(reply_markup=kb)
        else:
            await callback.answer("❌ ошибка удаления")

@router.callback_query(F.data.startswith("category:"))
async def show_category(callback: CallbackQuery):
    """показ рецептов по категории"""
    category = callback.data.split(":", 1)[1]
    
    await callback.message.edit_text(f"🔍 ищу рецепты в категории {category}...")
    
    recipes = await meal_api.get_by_category(category)
    
    if recipes:
        recipe = recipes[0]  # первый рецепт
        text = format_recipe(recipe)
        
        # сохраняем рецепт для пользователя
        user_id = callback.from_user.id
        user_recipes[user_id] = recipe
        
        is_fav = await is_favorite(user_id, recipe['idMeal'])
        kb = get_recipe_actions(recipe['idMeal'], is_fav)
        
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text(
            f"😔 не найдено рецептов в категории {category}",
            reply_markup=get_main_menu()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("show_fav_"))
async def show_favorite_recipe(callback: CallbackQuery):
    """показать избранный рецепт"""
    recipe_id = callback.data.replace("show_fav_", "")
    
    await callback.message.edit_text("🔍 загружаю рецепт...")
    
    recipe = await meal_api.get_by_id(recipe_id)
    
    if recipe:
        text = format_recipe(recipe)
        
        # сохраняем рецепт для пользователя
        user_id = callback.from_user.id
        user_recipes[user_id] = recipe
        
        # это точно избранный рецепт
        kb = get_recipe_actions(recipe_id, True)
        
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text(
            "😔 не удалось загрузить рецепт",
            reply_markup=get_main_menu()
        )
    
    await callback.answer()

@router.message(RecipeSearchFilter())
async def direct_search(message: Message):
    """прямой поиск без команды"""
    query = message.text.strip()
    
    # только если это не очень короткий запрос
    if len(query) < 3:
        return
    
    await message.answer("🔍 ищу рецепты...")
    
    recipes = await meal_api.search_by_name(query)
    
    if recipes:
        recipe = recipes[0]
        text = format_recipe(recipe)
        
        # сохраняем рецепт для пользователя
        user_id = message.from_user.id
        user_recipes[user_id] = recipe
        
        is_fav = await is_favorite(user_id, recipe['idMeal'])
        kb = get_recipe_actions(recipe['idMeal'], is_fav)
        
        await message.answer(text, reply_markup=kb)
    else:
        await message.answer(
            f"🤷‍♀️ не найдено рецептов по запросу '{query}'\n\nиспользуй /search для поиска или кнопки меню",
            reply_markup=get_main_menu()
        )