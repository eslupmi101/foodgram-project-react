from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["id", "recipe", "user"]
    list_filter = ["recipe", "user"]
    search_fields = ["recipe__name", "user__username"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "measurement_unit"]
    list_filter = ["name", "measurement_unit"]
    search_fields = ["name", "measurement_unit"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "author", "cooking_time",
        "recipes_ingredients", "favorite_count"
    ]
    list_filter = ["name", "author", "tags"]
    search_fields = ["name", "author__username", "cooking_time"]
    filter_horizontal = ["tags"]

    def favorite_count(self, obj):
        return obj.favorites.count()

    favorite_count.short_description = "Количество избранных"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "color", "slug"]
    list_filter = ["name", "color", "slug"]
    search_fields = ["name", "color", "slug"]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "recipe", "ingredient"]
    list_filter = ["recipe__name", "ingredient__name"]
    search_fields = ["recipe__name", "ingredient__name"]


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ["id", "recipe", "tag"]
    list_filter = ["recipe__name", "tag__name"]
    search_fields = ["recipe__name", "tag__name"]


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]
    list_filter = ["user", "recipe"]
    search_fields = ["user__username"]
