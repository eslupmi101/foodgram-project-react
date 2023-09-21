import base64
import logging

from django.contrib.auth import password_validation
from django.core.files.base import ContentFile
from recipes.models import (Ingredient, Recipe, RecipeIngredient, ShoppingCart,
                            Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from core.serializers import BaseUserSerializer
from users.models import User


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise ValidationError(
                {'current_password': 'Текущий пароль введен неверно.'}
            )

        return value

    def validate_new_password(self, value):
        user = self.context['request'].user

        try:
            password_validation.validate_password(value, user=user)
        except ValidationError as e:
            raise ValidationError({'new_password': e.messages})

        return value

    def update(self, instance, validated_data):
        user = instance
        new_password = validated_data['new_password']
        user.set_password(new_password)
        user.save()

        return user


class FavoriteRecipeGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]
        read_only_fields = fields


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name",
            "last_name", "is_subscribed", "password"
        ]
        read_only_fields = ["id", "is_subscribed"]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if "role" in validated_data and not request.user.is_admin:
            raise serializers.ValidationError(
                "You don't have permission to access this action",
                status.HTTP_403_FORBIDDEN
            )

        return super().update(instance, validated_data)

    def create(self, validated_data):    
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"]
        )
        try:
            shopping_cart = ShoppingCart.objects.create(
                owner=user
            )
            logging.debug(
                f"User {user.pk} created. "
                f"Shopping cart {shopping_cart.pk} for user created"
            )
        except CreateShoppingCartError as e:
            logging.error(
                f"User {user.pk} created. "
                f"Shopping cart cannot be created {e}."
            )

        return user

    def validate_username(self, username):
        if username == "me":
            raise serializers.ValidationError(
                "It is forbidden to use this name."
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "A user with this name already exists"
            )

        return username

    def validate_email(self, email):
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            raise serializers.ValidationError(
                "A user with this email already exists"
            )
        return email

    def to_representation(self, instance):
        if self.context.get('request').method == 'POST':
            self.fields.pop('is_subscribed', None)

        return super().to_representation(instance)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


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
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount", "name", "measurement_unit"]
        read_only_fields = ["name", "measurement_unit"]

    def get_name(self, object):
        return object.ingredient.name

    def get_measurement_unit(self, object):
        return object.ingredient.measurement_unit


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
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "author", "tags", "ingredients", "image",
            "name", "text", "cooking_time"
        ]
        read_only_fields = fields

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


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
    image = Base64ImageField(required=True)
    author = UserSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = [
            "id", "author", "tags", "ingredients", "image",
            "name", "text", "cooking_time",
            "is_favorited", "is_in_shopping_cart",
        ]
        read_only_fields = ["author"]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipes_ingredients")

        recipe = super().create(validated_data)

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get("ingredient")["id"],
                amount=ingredient.get("amount")
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("recipes_ingredients")
        recipe = super().update(instance, validated_data)

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get("ingredient")["id"],
                amount=ingredient.get("amount")
            )

        return recipe

    def get_is_in_shopping_cart(self, object):
        user = self.context.get("request").user

        if not user.is_authenticated:
            return False

        return ShoppingCart.objects.filter(
            recipes=object,
            owner=user
        ).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True)

    class Meta:
        model = ShoppingCart
        fields = ["recipes", "owner"]


class UserRecipeSerializer(BaseUserSerializer):
    recipes = RecipeSerializer(
        many=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name",
            "last_name", "is_subscribed", "recipes",
            "recipes_count"
        ]
        read_only_fields = [
            "id", "is_subscribed", "recipes", "recipes_count"
        ]

    def get_recipes_count(self, object):
        return Recipe.objects.filter(
            author=object
        ).count()
