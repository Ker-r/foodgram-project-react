import django_filters as filters

from .models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    favorite = filters.BooleanFilter(
        method='get_favorite'
    )
    shop = filters.BooleanFilter(
        method='get_shop'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'favorite', 'shop')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return Recipe.objects.all()

    def get_shop(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(purchases__user=user)
        return Recipe.objects.all()


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('title', )
