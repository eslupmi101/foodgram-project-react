from django.db import models
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField


class Favorite(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        verbose_name="Рецепт",
        related_name="favorites",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "users.User",
        verbose_name="Пользователь",
        related_name="favorites",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        ordering = ["id"]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Мера измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["id"]


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
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["id"]


class ShoppingCart(models.Model):
    recipes = models.ManyToManyField(
        "recipes.Recipe",
        through="ShoppingCartRecipe",
        related_name="shopping_carts",
        verbose_name="Рецепты"
    )
    owner = models.OneToOneField(
        "users.User",
        verbose_name="Владелец корзины покупок",
        related_name="shopping_carts",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name = "Корзины покупок"
        ordering = ["id"]


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    color = ColorField(
        verbose_name="Цветовой код",
        default='#FF0000'
    )
    slug = models.CharField(
        max_length=200,
        verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["id"]


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
    amount = models.PositiveIntegerField(
        verbose_name="Количество ингридиента",
        validators=[
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = "Соответствие рецепта и ингредиентов"
        verbose_name = "Соответствия рецепта и ингредиентов"
        ordering = ["id"]


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
        ordering = ["id"]


class ShoppingCartRecipe(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        verbose_name="Рецепт",
        related_name="shopping_carts_recipes",
        on_delete=models.CASCADE
    )
    shopping_cart = models.ForeignKey(
        "recipes.ShoppingCart",
        verbose_name="Корзина покупок",
        related_name="shopping_carts_recipes",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Соответствие корзины покупок и рецептов"
        verbose_name = "Соответствия корзины покупок и рецептов"
        ordering = ["id"]
