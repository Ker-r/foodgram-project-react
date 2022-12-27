from django.contrib import admin
from django.db.models import Count

from .models import (
    Ingredient,
    IngredientAmount,
    FavoriteRecipe,
    Recipe,
    Shop,
    Tag,
)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.TabularInline):
    model = IngredientAmount
    autocomplete_fields = ('ingredient', )


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmountAdmin,)
    list_display = (
        'id', 'name', 'author', 'description', 'pub_date', 'favorite_count'
    )
    search_fields = ('name', 'author', 'tag')
    list_filter = ('name', 'author', 'tag', 'pub_date')
    filter_vertical = ('tag',)
    empty_value_display = '-пусто-'

    def favorite_count(self, obj):
        return obj.obj_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            obj_count=Count(
                'recipe_favorite', distinct=True
            )
        )


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('recipe',)
    list_filter = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Tag, TagAdmin)
