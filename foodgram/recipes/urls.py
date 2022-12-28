from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DownloadShop, IngredientViewSet,
    RecipeViewSet, TagViewSet
)


router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShop.as_view()),
    path('', include(router.urls)),
]
