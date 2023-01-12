from django.db.models import F, Sum

from recipes.models import IngredientAmount


def get_list_ingredients(user):

    ingredients = IngredientAmount.objects.filter(
        recipe__shopping_recipe__user=user).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'amount', 'ingredient__measurement_unit')
    return ingredients
