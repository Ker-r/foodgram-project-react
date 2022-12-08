from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DownloadShop, FavoriteApiView, IngredientViewSet,
    RecipeViewSet, ShopViewSet, TagViewSet
)


router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShop.as_view()),
    path('', include(router.urls)),
    path('recipes/<int:favorite_id>/favorite/', FavoriteApiView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', ShopViewSet.as_view()),
]
