from django.contrib.auth import get_user_model
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from users.serializers import CurrentUserSerializer
from .models import (
    Ingredient, IngredientAmount, FavoriteRecipe, Recipe, Shop, Tag
)

User = get_user_model


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientNumderSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('__all__')


class AddIngredientNumderSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class RecipeImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    author = CurrentUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'favorite',
            'shop', 'name', 'image', 'text', 'cooking_time'
        )

    @staticmethod
    def get_ingredients(obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientNumderSerializer(ingredients, many=True).data

    def get_favorite(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return FavoriteRecipe.objects.filter(recipe=obj, user=user).exists()

    def get_shop(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Shop.objects.filter(recipe=obj, user=user).exists()


class RecipeFullSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CurrentUserSerializer(read_only=True)
    ingredients = AddIngredientNumderSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField()
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'ingredients', 'name',
            'text', 'cooking_time'
        )

    def validate(self, data):
        # ingredients = data.get('ingredients')
        # for ingredient in ingredients:
        #     if not Ingredient.objects.filter(
        #             id=ingredient['id']).exists():
        #         raise serializers.ValidationError(
        #             {'ingredients': '?????????????? ?????????????????????? ?????? ?? ????????'}
        #         )
        tags = data.get('tags')
        if len(tags) != len(set([item for item in tags])):
            raise serializers.ValidationError(
                {'tags': '???????? ???? ?????????? ??????????????????????'}
            )
        # if len(ingredients) != len(set([item['id'] for item in ingredients])):
        #     raise serializers.ValidationError(
        #         '?????????????????????? ???? ???????????? ??????????????????????'
        #     )
        cooking_time = data.get('cooking_time')
        if cooking_time > 300 or cooking_time < 1:
            raise serializers.ValidationError(
                {'cooking_time': '?????????? ?????????????????????????? ???? 1 ???? 300 ??????????'}
            )
        amount = data.get('ingredients')
        if [item for item in amount if item['amount'] < 1]:
            raise serializers.ValidationError(
                {'amount': '?????????????????????? ???????????????????? ???????????????????????? = 1'}
            )
        return data

    @staticmethod
    def add_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if IngredientAmount.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists():
                amount += F('amount')
            IngredientAmount.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        self.add_ingredients(ingredient_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientAmount.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)


class ShowFavoriteRecipeShopListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = FavoriteRecipe
        validators = [UniqueTogetherValidator(
            queryset=FavoriteRecipe.objects.all(),
            fields=('user', 'recipe'),
            message='???????????? ?????? ???????????????? ?? ??????????????????'
        )]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeImageSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShopSerializer(FavoriteSerializer):

    class Meta(FavoriteSerializer.Meta):
        mosel = Shop
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=Shop.objects.all(),
            fields=('user', 'recipe'),
            message='???????????? ?????? ???????????????? ?? ???????????? ??????????????'
        )]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeImageSerializer(
            instance.recipe,
            context={'request': request}
        ).data
