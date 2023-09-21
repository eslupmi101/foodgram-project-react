import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from core.exceptions import CreateShoppingCartError
from recipes.models import ShoppingCart

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        try:
            shopping_cart = ShoppingCart.objects.create(
                owner=instance
            )
            logging.debug(
                f"User {instance.pk} created. "
                f"Shopping cart {shopping_cart.pk} for user created"
            )
        except CreateShoppingCartError as e:
            logging.error(
                f"User {instance.pk} created. "
                f"Shopping cart cannot be created {e}."
            )
