from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser

User = CustomUser


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        null=False
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
        null=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit}).'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        null=False,
        verbose_name='Tag'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        default='#ffffff',
        verbose_name='Цвет тэга'
    )
    slug = models.SlugField(
        'Slug тега',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        null=False
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='media/'
    )
    text = models.TextField(
        max_length=2000,
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='ingredients',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tag',
        verbose_name='Тэг'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[MinValueValidator(1, 'Значение не может быть < 1')],
        default=1
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество больше нуля!',
        ),),
        verbose_name='Количество',
        help_text='Введите количество единиц ингредиента',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='recipe_ingredient_exists'),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'),
        )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} – {self.amount}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_favorite',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном пользователя {self.user}'


class Shop(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_user',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shopping_recipe_user_exists',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} у пользователя {self.user}'
