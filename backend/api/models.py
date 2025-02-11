from django.core import validators
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User
from backend.constants import (INGREDIENT_MIN_AMOUNT,
                               INGREDIENT_MIN_AMOUNT_ERROR, LEN_RECIPE_NAME,
                               LENG_MAX, MAX_COOKING_TIME,
                               MAX_LENG, MAX_NUMBER_OF_CHARACTERS,
                               MIN_COOKING_TIME)


class IngredientTagRecipe(models.Model):
    """Абстрактная модель. Добавляет название."""

    name = models.CharField(
        'Название',
        unique=True,
        max_length=LENG_MAX,
        help_text=MAX_NUMBER_OF_CHARACTERS
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        "Название тега",
        max_length=MAX_LENG,
        unique=True,
        help_text="Название тега, не более 32 символов.",
    )
    slug = models.SlugField(
        "Слаг тега",
        max_length=MAX_LENG,
        unique=True,
        help_text="Слаг тега, не более 32 символов.",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(IngredientTagRecipe):
    """Модель списка ингредиентов."""

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=LENG_MAX,
        help_text=MAX_NUMBER_OF_CHARACTERS
    )

    class Meta(IngredientTagRecipe.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return (
            f'{self.name} ({self.measurement_unit})'
        )


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        "Название рецепта",
        max_length=LEN_RECIPE_NAME,
        help_text="Название рецепта, не более 256 символов.",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="api/recipes/",
        help_text="Картинка рецепта.",
    )
    text = models.TextField(
        "Описание рецепта",
        help_text="Описание рецепта.",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления в минутах",
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ],
        help_text="Время приготовления в минутах от 1 до 32000.",
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Количество ингредиентов в рецепте.
    Модель связывает Recipe и Ingredient с указанием количества ингредиентов.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_list'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )

    amount = models.PositiveSmallIntegerField(
        default=INGREDIENT_MIN_AMOUNT,
        validators=(
            validators.MinValueValidator(
                INGREDIENT_MIN_AMOUNT,
                message=INGREDIENT_MIN_AMOUNT_ERROR
            ),
        ),
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'


class FavoriteAndShoppingCartModel(models.Model):
    """Абстрактная модель. Добавляет юзера и рецепт."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favourites(FavoriteAndShoppingCartModel):
    """Избранное."""
    pub_date = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]
