from django.db import models


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    image = models.ImageField(
        verbose_name="Картинка, закодированная в Base64",
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    author = models.ForeignKey(
        "users.User",
        verbose_name="Автор",
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )
    ingredients = models.ManyToManyField(
        "recipes.Ingredient",
        verbose_name="Список ингредиентов",
        through="RecipeIngredient"
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


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Количество с типом измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    color = models.CharField(
        max_length=200,
        verbose_name="Цветовой код"
    )
    slug = models.CharField(
        max_length=200,
        verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


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
