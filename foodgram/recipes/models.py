from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import CustomUser

User = CustomUser


class Ingredient(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        null=False
        )
    unit_measure = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
        null=False
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} ({self.unit_measure}).'


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
    images = models.ImageField(
        verbose_name='Картинка',
        upload_to='media/'
    )
    description = models.TextField(
        max_length=2000,
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredintsNumber',
        related_name='ingredients',
        verbose_name='Ингридиенты'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='tag',
        verbose_name='Тэг'
    )
    time_cook = models.PositiveSmallIntegerField(
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


class IngredintsNumber(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецептах'

    def __str__(self):
        return f'Количество {self.ingredient} в "{self.recipe}"'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        UniqueConstraint(fields=['recipe', 'user'], name='favorite_unique')

    def __str__(self):
        return f'Избранный рецепт: "{self.user}"'


class Shop(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buy',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='buy',
        verbose_name='Покупка'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'Покупка: "{self.user}"'
