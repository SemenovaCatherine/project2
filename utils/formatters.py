def format_recipe(recipe):
    """форматирует рецепт для отправки"""
    name = recipe.get('strMeal', 'без названия')
    category = recipe.get('strCategory', 'без категории')
    area = recipe.get('strArea', 'без региона')
    instructions = recipe.get('strInstructions', 'нет инструкций')
    
    # обрезаем инструкции если слишком длинные
    if len(instructions) > 500:
        instructions = instructions[:500] + "..."
    
    # ингредиенты
    ingredients = []
    for i in range(1, 21):
        ingredient = recipe.get(f'strIngredient{i}')
        measure = recipe.get(f'strMeasure{i}')
        if ingredient and ingredient.strip():
            if measure and measure.strip():
                ingredients.append(f"• {measure.strip()} {ingredient.strip()}")
            else:
                ingredients.append(f"• {ingredient.strip()}")
    
    ingredients_text = "\n".join(ingredients[:10])  # первые 10
    if len(ingredients) > 10:
        ingredients_text += f"\n... и еще {len(ingredients) - 10} ингредиентов"
    
    text = f"🍽 <b>{name}</b>\n\n"
    text += f"📂 категория: {category}\n"
    text += f"🌍 кухня: {area}\n\n"
    
    if ingredients:
        text += f"📝 <b>ингредиенты:</b>\n{ingredients_text}\n\n"
    
    text += f"👩‍🍳 <b>приготовление:</b>\n{instructions}"
    
    return text

def format_favorites_list(favorites):
    """форматирует список избранного"""
    if not favorites:
        return "🤷‍♀️ у вас пока нет избранных рецептов"
    
    text = "⭐ <b>ваши избранные рецепты:</b>\n\n"
    for i, recipe in enumerate(favorites, 1):
        text += f"{i}. {recipe['name']}\n"
    
    return text