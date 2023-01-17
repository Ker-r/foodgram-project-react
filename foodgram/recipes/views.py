import datetime
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from foodgram.pagination import LimitPageNumberPaginator
from .filters import IngredientFilter, RecipeFilter
from .models import (
    Ingredient, IngredientAmount,
    Recipe, Tag, Shop
)
from users.models import User
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from .serializers import (
    IngredientSerializer, RecipeSerializer,
    RecipeFullSerializer, TagSerializer
)
# from .services import download_file


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_classes = {
        'retrieve': RecipeSerializer,
        'list': RecipeSerializer,
    }
    default_serializer_class = RecipeFullSerializer
    permission_classes = (IsAuthorOrAdmin,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPaginator

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action,
                                           self.default_serializer_class)

    def _favorite_shopping_post_delete(self, related_manager):
        recipe = self.get_object()
        if self.request.method == 'DELETE':
            related_manager.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if related_manager.filter(recipe=recipe).exists():
            raise ValidationError('Рецепт уже в избранном')
        related_manager.create(recipe=recipe)
        serializer = RecipeSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def favorite(self, request, pk=None):
        return self._favorite_shopping_post_delete(
            request.user.favorite
        )

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def shopping_cart(self, request, pk=None):
        return self._favorite_shopping_post_delete(
            request.user.shopping_user
        )

    @action(methods=['get'], detail=False, url_path='download_shopping_cart')
    def load_shop_list(self, request):
        """Функция скачивания листа покупок в файле txt."""
        user = get_object_or_404(User, username=request.user)
        recipes_id = Shop.objects.filter(user=user).values('recipe')
        recipes = Recipe.objects.filter(pk__in=recipes_id)
        shop_dict = {}
        n_rec = 0
        for recipe in recipes:
            n_rec += 1
            ing_amounts = IngredientAmount.objects.filter(recipe=recipe)
            for ing in ing_amounts:
                if ing.ingredient.name in shop_dict:
                    shop_dict[ing.ingredient.name][0] += ing.amount
                else:
                    shop_dict[ing.ingredient.name] = [
                        ing.amount,
                        ing.ingredient.measurement_unit
                    ]
        now = datetime.datetime.now()
        now = now.strftime("%d-%m-%Y")
        shop_string = (
            f'FoodGram\nВыбрано рецептов: {n_rec}\
            \n-------------------\n{now}\
            \nСписок покупок:\
            \n-------------------'
        )
        for key, value in shop_dict.items():
            shop_string += f'\n{key} ({value[1]}) - {str(value[0])}'
        return HttpResponse(shop_string, content_type='text/plain')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    pagination_class = None
