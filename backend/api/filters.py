from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Название"
    )

    class Meta:
        model = Ingredient
        fields = ["name"]


class RecipeFilterSet(filters.FilterSet):
    author = filters.NumberFilter(
        field_name="author",
        lookup_expr="exact",
        label="Автор"
    )
    is_favorited = filters.BooleanFilter(
        field_name="is_favorited",
        lookup_expr="exact",
        label="В избранных"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name="is_in_shopping_cart",
        lookup_expr="exact",
        label="В корзине покупок"
    )
    tags = filters.CharFilter(
        field_name="tags__slug",
        lookup_expr="icontains",
        label="Теги"
    )

    class Meta:
        model = Recipe
        fields = [
            "author", "is_favorited", "is_in_shopping_cart", "tags__slug"
        ]
