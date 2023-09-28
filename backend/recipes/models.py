from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseRecipeUserModel


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Мера измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    image = models.ImageField(
        verbose_name="Картинка, закодированная в Base64",
        upload_to='recipes/images/'
    )
    author = models.ForeignKey(
        "users.User",
        verbose_name="Автор",
        related_name="recipes",
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    tags = models.ManyToManyField(
        "recipes.Tag",
        verbose_name="Список id тегов",
        through="RecipeTag"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[
            MinValueValidator(
                1,
                message="Минимальное время приготовления - 1 минута"
            ),
            MaxValueValidator(
                600,
                message=(
                    "Максимальное время приготовления"
                    " - 10 часов (600 минут)")
            ),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["pub_date"]

    def __str__(self) -> str:
        return self.name


class ShoppingCart(BaseRecipeUserModel):
    class Meta:
        verbose_name = "Рецепт в корзине покупок"
        verbose_name = "Рецепты в корзине покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_shopping_cart"
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Рецепт {str(self.recipe)} в корзине покупок"
            f"пользователя {str(self.user)}"
        )


class Favorite(BaseRecipeUserModel):
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_favorite"
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Избранный рецепт {str(self.recipe)}"
            f" пользователя {str(self.user)}"
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        unique=True
    )
    color = ColorField(
        verbose_name="Цветовой код",
        default='#FF0000',
        unique=True
    )
    slug = models.CharField(
        max_length=200,
        verbose_name="Слаг",
        unique=True
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.slug


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        verbose_name="Рецепт",
        related_name="recipes_ingredients",
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        "recipes.Ingredient",
        verbose_name="Ингредиент",
        related_name="recipes_ingredients",
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество ингредиента",
        validators=[
            MinValueValidator(
                1,
                message="Минимальное количество ингредиента - 1"
            ),
            MaxValueValidator(
                10000,
                message=(
                    "Максимальное количество ингредиента"
                    " - 10 000")
            ),
        ]
    )

    class Meta:
        verbose_name = "Соответствие рецепта и ингредиентов"
        verbose_name = "Соответствия рецепта и ингредиентов"

    def __str__(self) -> str:
        return (
            f"Соответствие рецепта {str(self.recipe)}"
            f"и ингредиента {str(self.ingredient)}"
        )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        verbose_name="Рецепт",
        related_name="recipes_tags",
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        "recipes.Tag",
        verbose_name="Тег",
        related_name="recipes_tags",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Соответствие рецепта и тегов"
        verbose_name = "Соответствия рецепта и тегов"

    def __str__(self) -> str:
        return (
            f"Соответствие рецепта {str(self.recipe)}"
            f" и тега {str(self.tag)}"
        )
