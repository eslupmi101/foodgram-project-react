from rest_framework import serializers


class IsSubscribedUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user

        if not user.is_authenticated:
            return False

        if user == obj:
            return False

        return bool(
            obj.subscribe_subscribers.filter(subscriber=user).exists()
        )
