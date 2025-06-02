import json
import os
import aiofiles
from config.settings import DATA_FILE

async def load_data():
    """загружает данные из файла"""
    if not os.path.exists(DATA_FILE):
        # создаем папку и файл
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        data = {"users": {}, "favorites": {}, "menus": {}}
        await save_data(data)
        return data
    
    try:
        async with aiofiles.open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except:
        return {"users": {}, "favorites": {}, "menus": {}}

async def save_data(data):
    """сохраняет данные в файл"""
    async with aiofiles.open(DATA_FILE, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))

async def add_user(user_id: int, username: str = None):
    """добавляет пользователя"""
    data = await load_data()
    user_key = str(user_id)
    
    if user_key not in data["users"]:
        data["users"][user_key] = {
            "username": username,
            "join_date": "now"
        }
        data["favorites"][user_key] = []
        data["menus"][user_key] = {}
        await save_data(data)

async def add_favorite(user_id: int, recipe):
    """добавляет рецепт в избранное"""
    data = await load_data()
    user_key = str(user_id)
    
    # проверяем что пользователь есть
    if user_key not in data["favorites"]:
        data["favorites"][user_key] = []
    
    # проверяем что рецепта еще нет
    recipe_data = {
        "id": recipe.get('idMeal'),
        "name": recipe.get('strMeal'),
        "category": recipe.get('strCategory'),
        "area": recipe.get('strArea')
    }
    
    # ищем дубликат
    for fav in data["favorites"][user_key]:
        if fav["id"] == recipe_data["id"]:
            return False  # уже есть
    
    data["favorites"][user_key].append(recipe_data)
    await save_data(data)
    return True

async def remove_favorite(user_id: int, recipe_id: str):
    """удаляет рецепт из избранного"""
    data = await load_data()
    user_key = str(user_id)
    
    if user_key in data["favorites"]:
        data["favorites"][user_key] = [
            fav for fav in data["favorites"][user_key] 
            if fav["id"] != recipe_id
        ]
        await save_data(data)
        return True
    return False

async def get_favorites(user_id: int):
    """получает избранные рецепты пользователя"""
    data = await load_data()
    user_key = str(user_id)
    return data["favorites"].get(user_key, [])

async def is_favorite(user_id: int, recipe_id: str):
    """проверяет есть ли рецепт в избранном"""
    favorites = await get_favorites(user_id)
    return any(fav["id"] == recipe_id for fav in favorites)

async def save_menu(user_id: int, day: str, recipe):
    """сохраняет рецепт в меню на день"""
    data = await load_data()
    user_key = str(user_id)
    
    if user_key not in data["menus"]:
        data["menus"][user_key] = {}
    
    data["menus"][user_key][day] = {
        "id": recipe.get('idMeal'),
        "name": recipe.get('strMeal'),
        "category": recipe.get('strCategory')
    }
    
    await save_data(data)

async def get_menu(user_id: int):
    """получает меню пользователя"""
    data = await load_data()
    user_key = str(user_id)
    return data["menus"].get(user_key, {})