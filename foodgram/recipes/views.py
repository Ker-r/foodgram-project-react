import datetime
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (
    FavoriteRecipe, Ingredient, IngredintsNumber,
    Recipe, Shop, Tag
)
from .permissions import IsOwnerOrRead
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeSerializer,
    RecipeFullSerializer, ShopSerializer, TagSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filter_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrRead, ]
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeFullSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    queryset = Tag.objects.all()
    pagination_class = None


class FavoriteApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, favorite_id):
        user = request.user
        data = {
            'recipe': favorite_id,
            'user': user.id
        }
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, favorite_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=favorite_id)
        FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'recipe': recipe_id,
            'user': user.id
        }
        serializer = ShopSerializer(
            data=data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Shop.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShop(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        shop_list = {}
        ingredients = IngredintsNumber.objects.filter(
            recipe__shop__user=request.user
        )
        for ingrediant in ingredients:
            quantity = ingrediant.quantity
            title = ingrediant.ingredient.title
            unit_measure = ingrediant.ingredient.unit_measure
            if title not in shop_list:
                shop_list[title] = {
                    'unit_measure': unit_measure,
                    'quantity': quantity
                }
            else:
                shop_list[title]['quantity'] += quantity
        main_list = ([f"* {item}:{value['quantity']}"
                      f"{value['unit_measure']}\n"
                      for item, value in shop_list.items()])
        today = datetime.date.today()
        main_list.append(f'\n Foodfram {today.year}')
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="ShopList.txt"'
        return response
