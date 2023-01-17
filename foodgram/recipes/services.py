def get_header_message(queryset):

    recipes_list = (', '.join([cart.recipe.name for cart in queryset]))
    return f'Вы добавили в корзину ингредиенты для: {recipes_list}.'


def get_total_list(queryset):

    total_list = {}

    for cart in queryset:
        r_ingredients = cart.recipe.recipe_ingredient.all()
        for r_ingredient in r_ingredients:
            name = r_ingredient.ingredient.name
            amount = r_ingredient.amount
            unit = r_ingredient.ingredient.measurement_unit
            if total_list.get(name) is None:
                total_list[name] = {unit: amount}
            else:
                total_list[name][unit] += amount
    return total_list
