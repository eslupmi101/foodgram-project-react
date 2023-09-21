from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Subscribe

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        abstract = True
    
    def get_is_subscribed(self, author):
        user = self.context.get("request").user

        if not user.is_authenticated:
            return False
        
        if user == author:
            return False

        return bool(
            Subscribe.objects.filter(
                author=author,
                subscriber=user
            ).exists()
        )
