from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Case, Value, When
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.utils import get_xls_recipes_file
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins

from users.models import Subscribe
from . import serializers
from .filters import IngredientFilterSet, RecipeFilterSet
from .permissions import RecipePermission, UserPermission

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [UserPermission]
    filterset_fields = ["username"]
    search_fields = ["username"]
    http_method_names = ["get", "post", "patch", "delete"]

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        url_path="me",
        url_name="Me",
        permission_classes=[IsAuthenticated]
    )
    def get_me(self, request):
        """
        Создает endpoint api/users/me/.

        Редактирования и получение
        данных собственного профиля
        """
        if request.method == "PATCH":
            serializer = serializers.UserSerializer(
                request.user,
                data=request.data,
                context={"request": request},
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # GET method
        serializer = serializers.UserSerializer(
            request.user,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=[IsAuthenticated]
    )
    def get_subscriptions(self, request):
        """
        Создает endpoint api/users/subscriptions/.

        Получение листа подписок.
        """
        authors = get_list_or_404(
            User,
            subscribe_subscribers_subscriber=request.user,
        )
        serializer = serializers.UserRecipeSerializer(
            authors,
            context={"request": request},
            many=True
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["DELETE", "POST"],
        url_path="subscribe",
        url_name="Subscribe",
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """
        Создает endpoint api/users/{id}/subscribe/.

        Управление подписками.
        """
        author = get_object_or_404(
            User,
            pk=pk
        )

        if author == request.user:
            return Response(
                data={"error": "You and author cannot be same user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscribe = Subscribe.objects.filter(
            author=author,
            subscriber=request.user
        )

        if request.method == "POST":
            if subscribe.exists():
                return Response(
                    data={
                        "error":
                        "You have already subscribed to this author."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.create(
                author=author,
                subscriber=request.user
            )

            serializer = serializers.UserRecipeSerializer(
                author,
                context={"request": request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        # DELETE method
        if not subscribe.exists():
            return Response(
                data={
                    "error":
                    "You are not subscribed to this author."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        subscribe.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="set_password",
        url_name="Set password",
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        """
        Создает endpoint api/users/set_password/.

        Смена пароля.
        """
        serializer = serializers.ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response(
            {"message": "Пароль успешно изменен."},
            status=status.HTTP_200_OK
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
    permission_classes = [RecipePermission]
    serializer_class = serializers.RecipeSerializer
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Case(
                    When(favorite__user=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

            queryset = queryset.annotate(
                is_in_shopping_cart=Case(
                    When(shoppingcart__user=user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

        return queryset

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
        recipes = Recipe.objects.filter(
            shoppingcart__user=self.request.user
        )
        if not recipes.exists():
            return Response(
                data={"error": "Shopping cart is blank."},
                status=status.HTTP_400_BAD_REQUEST
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
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
        url_name="Shopping cart"
    )
    def recipe_shopping_cart(self, request, pk=None):
        """
        Создает endpoint api/recipes/{id}/recipe_shopping_cart/.

        Управление рецептами из корзины покупок.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        recipe_shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe,
            user=user
        )

        if request.method == "POST":
            if recipe_shopping_cart.exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "error":
                        "The recipe is already in your shopping cart."
                    }
                )
            ShoppingCart.objects.create(
                recipe=recipe,
                user=user
            )
            serializer = serializers.RecipeGETSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        # DELETE method
        if not recipe_shopping_cart.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "error": "No recipe in shopping cart."
                }
            )
        recipe_shopping_cart.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
        url_name="Favorite"
    )
    def recipe_favorite(self, request, pk=None):
        """
        Создает endpoint api/recipes/{id}/favorite/.

        Управление рецептами из листа избранных.
        """
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )
        user = request.user

        favorite_queryset = Favorite.objects.filter(
            recipe=recipe,
            user=user
        )
        if request.method == "POST":
            if (
                favorite_queryset.exists()
            ):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "error": "Recipe is already in favorites."
                    }
                )
            Favorite.objects.create(
                recipe=recipe,
                user=user
            )
            serializer = serializers.FavoriteRecipeGETSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        # DELETE method
        if (
            not favorite_queryset.exists()
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "error": "No recipe in favorites."
                }
            )
        favorite_queryset.delete()
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
