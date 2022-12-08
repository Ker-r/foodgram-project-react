from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CurrentUserSerializer
from .models import (
    Ingredient, IngredintsNumber, FavoriteRecipe, Recipe, Shop, Tag
    )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientNumderSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True
    )
    name = serializers.SlugRelatedField(
        slug_field='name',
        source='ingredient', read_only=True
    )
    unit_measure = serializers.SlugRelatedField(
        slug_field='unit_measure',
        source='ingredient', read_only=True
    )

    class Meta:
        model = IngredintsNumber
        fields = ('__all__')


class AddIngredientNumderSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    number = serializers.IntegerField()

    class Meta:
        model = IngredintsNumber
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')
        lookup_field = 'id'
        extra_kwargs = {'url': {'lookup_field': 'id'}}


class RecipeSerializer(serializers.ModelSerializer):
    author = CurrentUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'favorite',
            'shop', 'name', 'description', 'time_cook'
        )

    def get_ingredient(self, obj):
        recipe = obj
        queryset = recipe.recipes_ingredient_list.all()
        return IngredientNumderSerializer(queryset, many=True).data

    def get_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_annonymous:
            return False
        user = request.user
        return FavoriteRecipe.objects.filter(recipe=obj, user=user).exists()

    def get_shop(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Shop.objects.filter(recipe=obj, user=user).exists()


class RecipeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'time_cook')

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)


class RecipeFullSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = CurrentUserSerializer(read_only=True)
    ingredients = AddIngredientNumderSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    time_cook = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'ingredients', 'name',
            'description', 'time_cook'
        )

    def create_bulk(self, recipe, ingredients_data):
        IngredintsNumber.objects.bulk_create(
            [IngredintsNumber(
                ingredient=ingredient['ingredient'],
                recipe=recipe,
                number=ingredient['number']
            ) for ingredient in ingredients_data]
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.create_bulk(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredintsNumber.objects.filter(recipe=instance).delete()
        self.create_bulk(instance, ingredients_data)
        instance.name = validated_data.pop('name')
        instance.description = validated_data.pop('description')
        instance.time_cook = validated_data.pop('time_cook')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for i in ingredients:
            if int(i['number']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Количество ингредиентов должно быть > 0')
                })
        return data

    def validate_time_cook(self, data):
        time_cook = self.initial_data.get('time_cook')
        if int(time_cook) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть > 0'
            )
        return data

    def representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = FavoriteRecipe
        validators = [UniqueTogetherValidator(
            queryset=FavoriteRecipe.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже добавлен в избранное'
        )]

    def representation(self, instance):
        request = self.context.get('request')
        return RecipeImageSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShopSerializer(FavoriteSerializer):

    class Meta:
        mosel = Shop
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=Shop.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже добавлен в список покупок'
        )]

    def representation(self, instance):
        request = self.context.get('request')
        return RecipeImageSerializer(
            instance.recipe,
            context={'request': request}
        ).data
