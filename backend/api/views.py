from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.utils import get_xls_recipes_file
from users.models import Subscribe
from . import serializers
from .filters import IngredientFilterSet, RecipeFilterSet
from .paginations import CustomPagination
from .permissions import (IsAuthenticatedReadOnlyOrAuthor,
                          ReadOnlyOrCreateUserOrUpdateProfile)


class UserViewSet(DjoserUserViewSet):
    permission_classes = [ReadOnlyOrCreateUserOrUpdateProfile]
    pagination_class = CustomPagination
    filterset_fields = ["username"]
    search_fields = ["username"]

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        url_name="Subscriptions",
        permission_classes=[IsAuthenticated]
    )
    def get_subscriptions(self, request):
        """
        Создает endpoint api/users/subscriptions/.

        Получение листа подписок.
        """
        queryset = self.get_queryset().filter(
            subscribe_authors__user=request.user,
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["POST"],
        url_path="subscribe",
        url_name="Subscribe",
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """
        Создает endpoint api/users/{id}/subscribe/.

        Управление подписками.
        """
        author = self.get_object()
        serializer = serializers.SubscribeSerializer(
            data={
                "author": author,
                "user": request.user
            },
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data["author"],
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = self.get_object()
        subscribe = get_object_or_404(
            Subscribe,
            user=request.user,
            author=author
        )
        subscribe.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filterset_class = IngredientFilterSet


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilterSet
    permission_classes = [IsAuthenticatedReadOnlyOrAuthor]
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(
            ingredients=self.request.data.get("ingredients"),
            author=self.request.user
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart",
        url_name="Download shopping cart"
    )
    def download_shopping_cart(self, request):
        """
        Создает endpoint api/recipes/download_shopping_cart/.

        Скачивание файла xls с информацией рецептов
        из корзины покупок.
        """
        recipes = get_list_or_404(
            Recipe,
            shoppingcart__user=self.request.user
        )

        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = (
            'attachment; filename="shopping-list.xls"'
        )
        response["Content-Type"] = "application/ms-excel; charset=utf-8"

        workbook = get_xls_recipes_file(recipes)
        workbook.save(response)
        return response

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
        url_name="Shopping cart"
    )
    def recipe_shopping_cart(self, request, pk=None):
        """
        Создает endpoint api/recipes/{pk}/recipe_shopping_cart/.

        Управление рецептами из корзины покупок.
        """
        recipe = self.get_object()
        serializer = serializers.ShopingCartSerializer(
            data={
                "recipe": recipe,
                "user": request.user
            },
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data["recipe"],
            status=status.HTTP_201_CREATED
        )

    @recipe_shopping_cart.mapping.delete
    def delete_recipe_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        shopping_cart = get_object_or_404(
            ShoppingCart,
            recipe=recipe,
            user=request.user
        )
        shopping_cart.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
        url_name="Favorite"
    )
    def recipe_favorite(self, request, pk=None):
        """
        Создает endpoint api/recipes/{pk}/favorite/.

        Управление рецептами из листа избранных.
        """
        recipe = self.get_object()
        serializer = serializers.FavoriteRecipSerializer(
            data={
                "recipe": recipe,
                "user": request.user
            },
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data["recipe"],
            status=status.HTTP_201_CREATED
        )

    @recipe_favorite.mapping.delete
    def delete_recipe_favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = get_object_or_404(
            Favorite,
            recipe=recipe,
            user=request.user
        )
        favorite.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]
