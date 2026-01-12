from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.module_loading import import_string
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied

from .email_templates import OTP_EMAIL_TEMPLATE, WELCOME_EMAIL_TEMPLATE

from datetime import timedelta
import secrets
import re

from .signals import otp_verified, create_profile
from .throttles import UserAuthThrottle, OTPVerifyThrottle
from .serializers import LoginSerializer

User = get_user_model()
UserSerializer = import_string(settings.USER_SERIALIZER)

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5


def generate_otp(length=OTP_LENGTH):
    return ''.join(secrets.choice("0123456789") for _ in range(length))


def send_otp_email(email, otp):
    subject = "کد تأیید پلتفورم هوشمند خدمت"
    formatted_otp = ' '.join([otp[i:i+3] for i in range(0, len(otp), 3)])
    html_content = OTP_EMAIL_TEMPLATE.format(
        otp=formatted_otp,
        expiry_minutes=OTP_EXPIRY_MINUTES,
        current_year=timezone.now().year
    )
    try:
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=f"کد تأیید شما: {otp} (معتبر تا {OTP_EXPIRY_MINUTES} دقیقه)",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        send_mail(
            subject="OTP Verification",
            message=f"Your OTP code is: {otp}. Valid for {OTP_EXPIRY_MINUTES} minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
        return False


def send_welcome_email(user):
    subject = f"خوش آمدید به پلتفورم هوشمند خدمت، {user.first_name or user.username}!"
    
    html_content = WELCOME_EMAIL_TEMPLATE.format(
        username=user.first_name or user.username,
        email=user.email,
        phone=user.phone,
        current_year=timezone.now().year
    )
    
    try:
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=f"Welcome {user.first_name or user.username}! Your account has been successfully created.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        send_mail(
            subject="Welcome to Our Platform!",
            message=f"Hi {user.first_name or user.username},\n\nYour account has been successfully created!\n\nUsername: {user.username}\nEmail: {user.email}\nPhone: {user.phone}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return False

class ResetPasswordView(APIView):
    def post(self, request):
        # get user data
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        confirm_new_password = request.data.get("confirm_new_password")

        # if user has not provided credentials send an error message
        if not email or not otp or not new_password:
            return Response(
                {"message": "Make sure you have filled all the fields correctly!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        # if entered passwords are not matching
        if new_password != confirm_new_password:
            return Response(
                {"message": "Entered passwords are not matching"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        # try to get the user by email provided
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid email"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        # if the user has not requested for password reset
        if not user.otp:
            return Response(
                {"error": "No OTP requested for this account"},
                status=status.HTTP_400_BAD_REQUEST
                )
        
        # if the OTP code is expired
        expiration_time = user.otp_created_at + timedelta(minutes=5)
        if timezone.now() > expiration_time:
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response(
                {"error": "OTP expired. Request a new one."},
                status=status.HTTP_400_BAD_REQUEST
                )
        
        # when the user sends wrong OTP code.
        if user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        # all cases are true and we set new password for user
        user.set_password(new_password)
        user.otp = None
        user.otp_created_at = None
        user.save()

        # delete the previous authentication token of user if exist
        Token.objects.filter(user=user).delete()
        return Response(
            {"message": "Password reset successfully!"}, 
            status=status.HTTP_200_OK
            )


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        # if the form is submited empty(without email)
        if not email:
            return Response(
                {"message": "Email is required!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        # try to get the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "No user found with this email, please enter a valid email address"}
                ,status=status.HTTP_400_BAD_REQUEST
                )
        
        # generate OTP for user, and set the OTP creation time
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # send the OTP code to user via email
        send_mail(
            subject="Password reset",
            message=f"Your OTP code for password reset is: {otp}. It is valid for 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    # only authenticated users can send request to this view
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user

        # get the user's data
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_new_password = request.data.get("confirm_new_password")

        # if the old password is not provided by user
        if not old_password:
            return Response({
                "message": "Old password is required!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # if new_password and confirm_new_password are not matching
        if new_password != confirm_new_password:
            return Response({
                "message": "Passwords are not matching!"
            },status=status.HTTP_400_BAD_REQUEST)
        
        # if the old password is entered wrong
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # set the user's password and save it to database
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully!"}, status=status.HTTP_200_OK)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user must be authenticated
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
            return Response({"message": "Logged out!"}, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied("You must be logged in to log out.")


class LoginView(APIView):
    MAX_ATTEMPTS = 5
    LOCKOUT_TIME = timedelta(minutes=5)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"message": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use email to fetch user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check lockout
        if user.lockout_until and timezone.now() < user.lockout_until:
            return Response(
                {"message": "Account temporarily locked. Try again later."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check OTP verification
        if not user.is_verified:
            return Response(
                {"message": "Account is not verified."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Authenticate using backend (email-based)
        authenticated_user = authenticate(
            request,
            username=email,   # still passed as username internally
            password=password
        )

        if not authenticated_user:
            user.faild_attempts += 1

            if user.faild_attempts >= self.MAX_ATTEMPTS:
                user.lockout_until = timezone.now() + self.LOCKOUT_TIME
                user.faild_attempts = 0
                user.save()

                return Response(
                    {"message": "Too many failed attempts. Account locked for 5 minutes."},
                    status=status.HTTP_403_FORBIDDEN
                )

            user.save()
            return Response(
                {"message": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Successful login
        user.faild_attempts = 0
        user.lockout_until = None
        user.save()

        # Refresh token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        serializer = UserSerializer(user)

        return Response({
            "token": token.key,
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    

class RegisterView(APIView):
    @transaction.atomic
    def post(self, request, role):

        data = request.data.copy()
        data["role"] = role

        user_exists = User.objects.filter(email=data.get("email")).exists()

        # if user_exists:

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate a 6-digit numeric OTP
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.is_verified = False

            if role == "admin":
                user.is_superuser = True
                user.is_staff = True

            user.save()

            # Send OTP to user's email
            send_otp_email(email=request.data.get("email"), otp=otp)

            return Response({
                "message": "User registered successfully! Check your email for OTP verification."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    # throttle_classes = [OTPVerifyThrottle]
    
    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
            print("user: ", user)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.otp:
            return Response(
                {"error": "No OTP found. Please request a new one."}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        # Check if OTP is expired (5 minutes)
        expiration_time = user.otp_created_at + timedelta(minutes=5)
        if timezone.now() > expiration_time:
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response({
                "error": "OTP has expired. Please request a new one."}, 
                status=status.HTTP_400_BAD_REQUEST
                )

        # Verify OTP
        if user.otp == otp_input:
            user.is_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            
            # send a success email to the user upon successfully creation of account
            otp_verified.send(sender=User, user=user)

            # create associated user's profile
            create_profile.send(sender=User, user=user)

            return Response(
                {"message": "You account has been verified successfully!"},
                status=status.HTTP_200_OK
                )
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
