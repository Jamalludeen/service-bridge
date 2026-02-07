from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

from .email_templates import WELCOME_EMAIL_TEMPLATE
from .signals import otp_verified, create_profile
from professional.models import Professional
from customer.models import CustomerProfile, Cart

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


@receiver(create_profile)
def create_user_profile(sender, user, **kwargs):
    if user.role == "professional":
        Professional.objects.create(user=user)
    
    if user.role == "customer":
        customer = CustomerProfile.objects.create(user=user)
        Cart.objects.create(customer=customer)
    
    