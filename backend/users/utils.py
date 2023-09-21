from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from .models import User


def send_email_confirmation(user: User):
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Confirm Your Registration'
    message = f'Your confirmation code is: {confirmation_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
