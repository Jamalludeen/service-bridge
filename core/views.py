from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.module_loading import import_string
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from datetime import timedelta
import random


User = get_user_model()
UserSerializer = import_string(settings.USER_SERIALIZER)


class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"message": "Logged out!"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        # get the user object requested
        user_obj = get_object_or_404(User, username=request.data.get("username"))

        # check if user exist in database and the account is verified with OTP code
        if user_obj and user_obj.is_verified:

            # if the user's provided password is invalid, send a message for user
            if not user_obj.check_password(request.data.get("password")):
                return Response({
                    "message":"Invalid credentials"
                },status=status.HTTP_400_BAD_REQUEST)
            
            """
            The regeneration/deletion of tokens on each login and the deletion on each logout
            is to improve system security/decrease security risks
            """
            # delete the previous token that was generated for the user
            Token.objects.filter(user=user_obj).delete()

            # generate new token eveytime user login to the system
            token, _ = Token.objects.get_or_create(user=user_obj)
            serializer = UserSerializer(instance=user_obj)
            return Response({"token": token.key,"user": serializer.data})
    
        return Response({"message":"Your account is not verfied!"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate a 6-digit numeric OTP
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.is_verified = False
            user.save()

            # Send OTP to user's email
            send_mail(
                subject="Verify your email",
                message=f"Your verification OTP code is: {otp}. It expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({
                "message": "User registered successfully! Check your email for OTP verification."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.otp:
            return Response({"error": "No OTP found. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP is expired (5 minutes)
        expiration_time = user.otp_created_at + timedelta(minutes=5)
        if timezone.now() > expiration_time:
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if user.otp == otp_input:
            user.is_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
