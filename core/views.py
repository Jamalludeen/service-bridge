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
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from datetime import timedelta
import secrets


User = get_user_model()
UserSerializer = import_string(settings.USER_SERIALIZER)

OTP_LENGTH = 6


def generate_otp(length=OTP_LENGTH):
    return ''.join(secrets.choice("0123456789") for _ in range(length))



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
        # otp = str(random.randint(100000, 999999))
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
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"message": "Logged out!"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    MAX_ATTEMPTS = 5
    LOCKOUT_TIME = timedelta(minutes=5)

    def post(self, request):
        # get the user object requested
        user = get_object_or_404(User, username=request.data.get("username"))

        # if the user try to login when his/her account is locked
        if user.lockout_until and timezone.now() < user.lockout_until:
            remaining = (user.lockout_until - timezone.now()).seconds // 60
            return Response(
                {"message": f"Account locked. Try again after {remaining} minutes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # if the user account is not verfied with OTP
        if not user.is_verified:
            return Response({"message": "Your account is not verified!"}, status=400)

        password = request.data.get("password")

        # if the password entered is wrong
        if not user.check_password(password):
            # increase the number of failed attempts
            user.faild_attempts += 1

            # if the failed attempts reaches to maximum
            if user.faild_attempts >= self.MAX_ATTEMPTS:
                # set the lock time for user
                user.lockout_until = timezone.now() + self.LOCKOUT_TIME
                # reset the failed attempts after locking
                user.failed_attempts = 0
                user.save()

                return Response(
                    {"message": "Too many failed attempts. Your account is locked for 5 minutes."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # if the failed login don't reach to maximum 
            user.save()
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        

        # password is correct -> reset attempts
        user.failed_attempts = 0
        user.lockout_until = None
        user.save()

        # Refresh token on login
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)

        serializer = UserSerializer(instance=user)

        return Response({
            "token": token.key,
            "user": serializer.data
        }, status=200)



class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data.copy()
        
        # As this view register only customers, we always set the role to customer 
        try:
            data.pop("role")
        except KeyError:
            data["role"] = "customer"

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate a 6-digit numeric OTP
            # otp = str(random.randint(100000, 999999))
            otp = generate_otp()
            print("otp in registration: ", otp)
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
            return Response(
                {"message": "You account has been verified successfully!"}, 
                status=status.HTTP_200_OK
                )
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
