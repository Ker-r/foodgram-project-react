from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram.pagination import LimitPageNumberPaginator
from .filters import IngredientFilter, RecipeFilter
from .models import (
    Ingredient, IngredientAmount,
    Recipe, Tag
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from .serializers import (
    IngredientSerializer, RecipeSerializer,
    RecipeFullSerializer, TagSerializer, RecipeImageSerializer
)
from .services import download_file


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
        serializer = RecipeImageSerializer(instance=recipe)
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    pagination_class = None


class DownloadShop(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__shop__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').order_by(
                    'ingredient__name').annotate(
                        ingredient_total=Sum('amount'))
        return download_file(ingredients)
