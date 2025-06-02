from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    """главное меню"""
    kb = [
        [
            InlineKeyboardButton(text="🔍 поиск рецептов", callback_data="search_recipes"),
            InlineKeyboardButton(text="🎲 случайный рецепт", callback_data="random_recipe")
        ],
        [
            InlineKeyboardButton(text="⭐ избранное", callback_data="show_favorites"),
            InlineKeyboardButton(text="📅 меню на неделю", callback_data="weekly_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_recipe_actions(recipe_id: str, is_favorite: bool = False, from_favorites: bool = False):
    """действия с рецептом"""
    kb = []
    
    if is_favorite:
        kb.append([InlineKeyboardButton(text="❌ убрать из избранного", callback_data=f"remove_fav_{recipe_id}")])
    else:
        kb.append([InlineKeyboardButton(text="⭐ в избранное", callback_data=f"add_fav_{recipe_id}")])
    
    if from_favorites:
        kb.append([InlineKeyboardButton(text="⬅️ к избранному", callback_data="show_favorites")])
    else:
        kb.append([InlineKeyboardButton(text="🔙 назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_categories_menu():
    """меню категорий"""
    kb = [
        [
            InlineKeyboardButton(text="🥩 мясо", callback_data="category:Beef"),
            InlineKeyboardButton(text="🐔 курица", callback_data="category:Chicken")
        ],
        [
            InlineKeyboardButton(text="🐟 рыба", callback_data="category:Seafood"),
            InlineKeyboardButton(text="🥗 вегетарианское", callback_data="category:Vegetarian")
        ],
        [
            InlineKeyboardButton(text="🍰 десерты", callback_data="category:Dessert"),
            InlineKeyboardButton(text="🔙 назад", callback_data="back_to_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_favorites_menu(favorites):
    """меню избранного с кнопками рецептов"""
    if not favorites:
        kb = [[InlineKeyboardButton(text="🔙 назад", callback_data="back_to_menu")]]
        return InlineKeyboardMarkup(inline_keyboard=kb)
    
    kb = []
    # показываем первые 5 рецептов
    for i, recipe in enumerate(favorites[:5]):
        name = recipe['name'][:30] + ('...' if len(recipe['name']) > 30 else '')
        recipe_id = recipe['id']
        
        kb.append([InlineKeyboardButton(
            text=f"{i+1}. {name}", 
            callback_data=f"show_fav_{recipe_id}"
        )])
    
    kb.append([InlineKeyboardButton(text="🔙 назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)