from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from .validators import UsernameValidator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия"
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        max_length=254,
    )

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer.'
                    ' Letters, digits and @/./+/-/_ only.'),
        validators=[
            UsernameValidator(
                regex=r'^[\w.@+-]+$',
            ),
            RegexValidator(
                regex=r'^(?!me$)',
                message=_('Username cannot be "me".')
            )
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    author = models.ForeignKey(
        "users.User",
        verbose_name="Автор",
        related_name="subscribe_authors",
        on_delete=models.CASCADE
    )
    subscriber = models.ForeignKey(
        "users.User",
        verbose_name="Подписчик",
        related_name="subscribe_subscribers",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author_id", "subscriber_id"],
                name="unique_subscriber"
            ),
            models.CheckConstraint(
                check=~Q(author_id=F("subscriber_id")),
                name="cannot_subscribe_yourself"
            )
        ]

    def __str__(self) -> str:
        return (
            f"Подписка {str(self.subscriber)}"
            f" на {str(self.author)}"
        )
