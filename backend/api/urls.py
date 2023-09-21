from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    'ingredients',
    views.IngredientViewSet,
    basename='recipes'
)
router.register(
    'recipes',
    views.RecipeViewSet,
    basename='recipes'
)
router.register(
    'tags',
    views.TagViewSet,
    basename='tags'
)
router.register(
    'users',
    views.UserViewSet,
    basename='users'
)


urlpatterns = [
    path('', include(router.urls))
]
