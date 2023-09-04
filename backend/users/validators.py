from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    def get_invalid_characters(self, value):
        invalid_characters = filter(lambda c: not self.regex.match(c), value)
        return "".join(invalid_characters)

    def __call__(self, value):
        if not self.regex.match(value):
            invalid_characters = self.get_invalid_characters(value)
            raise ValidationError(
                f'Invalid characters found: {invalid_characters}',
                code='invalid_username'
            )
