from django.db import models


class BaseRecipeUserModel(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        verbose_name="Рецепт",
        related_name="%(model_name)s",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "users.User",
        verbose_name="Пользователь",
        related_name="%(model_name)s",
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        default_related_name = "%(app_label)s_%(model_name)s"
