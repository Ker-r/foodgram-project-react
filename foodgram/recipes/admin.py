from django.contrib import admin

from .models import (
    Ingredient,
    IngredintsNumber,
    FavoriteRecipe,
    Recipe,
    Shop,
    Tag,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'unit_measure',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count',)
    list_filter = ('name', 'author', 'tag',)
    empty_value_display = '-пусто-'

    def count(self, obj):
        return obj.favorite_recipes.count()
    count.short_description = 'Количество добавленного в избранное'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredintsNumber)
admin.site.register(FavoriteRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Shop)
admin.site.register(Tag)
