from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribe, User


class UserGETSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name",
            "last_name", "is_subscribed"
        ]
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return bool(
            user.is_authenticated
            and Subscribe.objects.filter(
                author=obj,
                user=user
            ).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient.id",
        required=True
    )
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount", "name", "measurement_unit"]
        read_only_fields = ["name", "measurement_unit"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]
        read_only_fields = fields


class RecipeGETSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True
    )
    ingredients = RecipeIngredientSerializer(
        source="recipes_ingredients",
        required=True,
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "author", "tags", "ingredients", "image",
            "name", "text", "cooking_time"
        ]
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True
    )
    ingredients = RecipeIngredientSerializer(
        source="recipes_ingredients",
        required=True,
        many=True
    )
    image = Base64ImageField()
    author = UserGETSerializer(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id", "author", "tags", "ingredients", "image",
            "name", "text", "cooking_time",
            "is_favorited", "is_in_shopping_cart",
        ]
        read_only_fields = ["author", "is_favorited", "is_in_shopping_cart"]

    def create(self, validated_data):
        recipes_ingredients_data = validated_data.pop("recipes_ingredients")
        recipe = super().create(validated_data)

        self.__add_ingredients_to_recipe(
            recipes_ingredients_data,
            recipe
        )
        return recipe

    def update(self, instance, validated_data):
        recipes_ingredients_data = validated_data.pop("recipes_ingredients")

        self.__add_ingredients_to_recipe(
            recipes_ingredients_data,
            instance
        )
        return super().update(instance, validated_data)

    def __add_ingredients_to_recipe(
            self,
            recipes_ingredients_data: list[dict],
            recipe: Recipe
    ):
        for recipe_ingredient in recipes_ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=recipe_ingredient["ingredient"]["id"],
                amount=recipe_ingredient["amount"]
            )


class UserRecipeGETSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(
        many=True,
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name",
            "last_name", "is_subscribed", "recipes",
            "recipes_count"
        ]
        read_only_fields = fields

    def get_recipes_count(self, object):
        return Recipe.objects.filter(
            author=object
        ).count()

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user

        if not user.is_authenticated:
            return False

        if user == obj:
            return False

        return bool(
            obj.subscribe_authors.filter(user=user).exists()
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]
        read_only_fields = fields


class SubscribeSerializer(serializers.ModelSerializer):
    author = UserRecipeGETSerializer()

    class Meta:
        model = Subscribe
        fields = ["author", "user"]

    def to_internal_value(self, data):
        type_author = data.get("author")
        type_user = data.get("user")

        if not isinstance(type_author, User):
            raise ValidationError(
                {"author":
                 f"Invalid data. Expected a User, but got {type_author}."}
            )

        if not isinstance(type_user, User):
            raise ValidationError(
                {"user":
                 f"Invalid data. Expected a User, but got {type_user}."}
            )

        return data

    def validate(self, attrs):
        author = attrs.get("author")
        subscriber = attrs.get("user")

        is_subscribe_exists = Subscribe.objects.filter(
            author=author,
            user=subscriber
        ).exists()

        if author == subscriber:
            raise ValidationError("Вы не можете подписаться на самого себя.")

        if is_subscribe_exists:
            raise ValidationError(f"Вы уже подписаны на {str(author)}.")

        return super().validate(attrs)


class FavoriteRecipSerializer(serializers.ModelSerializer):
    recipe = ShortRecipeSerializer()

    class Meta:
        model = Favorite
        fields = ["recipe", "user"]

    def to_internal_value(self, data):
        type_recipe = data.get("recipe")
        type_user = data.get("user")

        if not isinstance(type_recipe, Recipe):
            raise ValidationError(
                {"recipe":
                 f"Invalid data. Expected a Recipe, but got {type_recipe}."}
            )

        if not isinstance(type_user, User):
            raise ValidationError(
                {"user":
                 f"Invalid data. Expected a User, but got {type_user}."}
            )

        return data

    def validate(self, attrs):
        user = attrs["user"]
        recipe = attrs["recipe"]

        if (
            Favorite.objects.filter(
                recipe=recipe,
                user=user
            ).exists()
        ):
            raise ValidationError(
                f"Вы уже добавили рецепт {recipe.name} в избранные."
            )

        return super().validate(attrs)


class ShopingCartSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = ShoppingCart
        fields = ["recipe", "user"]

    def to_internal_value(self, data):
        type_recipe = data.get("recipe")
        type_user = data.get("user")

        if not isinstance(type_recipe, Recipe):
            raise ValidationError(
                {"recipe":
                 f"Invalid data. Expected a Recipe, but got {type_recipe}."}
            )

        if not isinstance(type_user, User):
            raise ValidationError(
                {"user":
                 f"Invalid data. Expected a User, but got {type_user}."}
            )

        return data

    def validate(self, attrs):
        user = attrs["user"]
        recipe = attrs["recipe"]

        if (
            ShoppingCart.objects.filter(
                recipe=recipe,
                user=user
            ).exists()
        ):
            raise ValidationError(
                f"Вы уже добавили рецепт {recipe.name} в корзину покупок."
            )

        return super().validate(attrs)
