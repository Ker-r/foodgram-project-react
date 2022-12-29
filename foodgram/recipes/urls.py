from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DownloadShop, IngredientViewSet,
    RecipeViewSet, TagViewSet
)


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShop.as_view()),
    path('', include(router.urls)),
]
