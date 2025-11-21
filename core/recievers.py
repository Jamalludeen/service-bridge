from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .signals import otp_verified

@receiver(otp_verified)
def send_success_email(sender, user, **kwargs):
    username: str = user.username
    send_mail(
        subject="Account Created Successfully!",
        message=f"Congratulations {username.capitalize()}, Your account has been created successfully!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
