from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

from .email_templates import WELCOME_EMAIL_TEMPLATE
from .signals import otp_verified

@receiver(otp_verified)
def send_success_email(sender, user, **kwargs):
    username: str = user.username
    subject = f"خوش آمدید به پلتفورم هوشمند خدمت، {username.capitalize()}!"

    html_content = WELCOME_EMAIL_TEMPLATE.format(
        username=username.capitalize(),
        current_year=timezone.now().year
    )

    email_msg = EmailMultiAlternatives(
        subject=subject,
        body=f"Welcome {username}! Your account has been successfully created.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    
    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send()
