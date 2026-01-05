from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.module_loading import import_string
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache


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

from .signals import otp_verified
from .throttles import UserAuthThrottle, OTPVerifyThrottle

User = get_user_model()
UserSerializer = import_string(settings.USER_SERIALIZER)

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
REGISTRATION_CACHE_PREFIX = "reg_"
AUTH_SESSION_PREFIX = "auth_session_"
AUTH_SESSION_TIMEOUT = 900  # 15 minutes
MAX_OTP_ATTEMPTS = 5
MIN_OTP_RESEND_INTERVAL = 30  # seconds


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

def get_registration_data(email):
    cache_key = f"{REGISTRATION_CACHE_PREFIX}{email}"  # No role in key
    return cache.get(cache_key)


def validate_afg_phone(phone):
    pattern = r'^07\d{8}$'
    return re.match(pattern, phone) is not None


def get_user_response_data(user):
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "is_verified": user.is_verified
    }


def create_auth_token(user):
    """Create or get authentication token for user"""
    Token.objects.filter(user=user).delete()
    token, _ = Token.objects.get_or_create(user=user)
    return token


def create_auth_session(email, role):
    """Create authentication session and return session ID"""
    session_id = secrets.token_urlsafe(32)
    cache_key = f"{AUTH_SESSION_PREFIX}{session_id}"

    user_exists = User.objects.filter(email=email).exists()
    user_id = None

    if user_exists:
        user = User.objects.get(email=email)
        user_id = user.id

    session_data = {
        'email': email,
        'role': role,
        'user_exists': user_exists,
        'user_id': user_id,
        'step': 'email_submitted',
        'created_at': timezone.now().isoformat(),
        'otp_attempts': 0,
    }

    cache.set(cache_key, session_data, AUTH_SESSION_TIMEOUT)
    return session_id, session_data


def get_auth_session(session_id):
    """Retrieve authentication session data"""
    cache_key = f"{AUTH_SESSION_PREFIX}{session_id}"
    return cache.get(cache_key)


def update_auth_session(session_id, updates):
    """Update authentication session with new data"""
    cache_key = f"{AUTH_SESSION_PREFIX}{session_id}"
    session_data = cache.get(cache_key)

    if not session_data:
        return False

    session_data.update(updates)
    cache.set(cache_key, session_data, AUTH_SESSION_TIMEOUT)
    return True


def clear_auth_session(session_id):
    """Clear authentication session from cache"""
    cache_key = f"{AUTH_SESSION_PREFIX}{session_id}"
    cache.delete(cache_key)


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
    throttle_classes = [UserAuthThrottle]

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
            expiry_minutes = 5
            current_year = timezone.now().year

            html_content = OTP_EMAIL_TEMPLATE.format(
                otp=otp,
                expiry_minutes=expiry_minutes,
                current_year=current_year
            )

            text_content = (
                f"Your OTP code is {otp}"
                f"It will expire in {expiry_minutes} minutes."
            )

            email = EmailMultiAlternatives(
                subject="Verify your  email address",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            return Response({
                "message": "User registered successfully! Check your email for OTP verification."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    throttle_classes = [OTPVerifyThrottle]
    
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

            return Response(
                {"message": "You account has been verified successfully!"},
                status=status.HTTP_200_OK
                )
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# NEW UNIFIED AUTHENTICATION FLOW WITH 2FA
# ============================================================================

class InitiateAuthView(APIView):
    """Step 1: User enters email, OTP is sent"""
    throttle_classes = [UserAuthThrottle]

    def post(self, request, role):
        from .serializers import InitiateAuthSerializer

        serializer = InitiateAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        # Create session
        session_id, session_data = create_auth_session(email, role)

        # Generate and store OTP
        otp = generate_otp()

        if session_data['user_exists']:
            # Existing user - store OTP on user
            user = User.objects.get(id=session_data['user_id'])
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
        else:
            # New user - create temporary user with is_verified=False
            user = User.objects.create(
                email=email,
                username=f"temp_{secrets.token_hex(8)}",  # Temporary username
                role=role,
                is_verified=False
            )
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            # Update session with user_id
            update_auth_session(session_id, {'user_id': user.id})

        # Send OTP email
        send_otp_email(email, otp)

        return Response({
            'session_id': session_id,
            'user_exists': session_data['user_exists'],
            'message': 'OTP sent to your email',
            'next_step': 'verify_otp'
        }, status=status.HTTP_200_OK)


class VerifyAuthOTPView(APIView):
    """Step 2: User verifies OTP"""
    throttle_classes = [OTPVerifyThrottle]

    def post(self, request):
        from .serializers import VerifyOTPSerializer

        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        session_id = serializer.validated_data['session_id']
        otp = serializer.validated_data['otp']

        # Get session
        session_data = get_auth_session(session_id)
        if not session_data:
            return Response(
                {'message': 'Invalid or expired session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user and verify OTP
        try:
            user = User.objects.get(id=session_data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check OTP exists
        if not user.otp:
            return Response(
                {'message': 'No OTP found. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check OTP expiry
        otp_age = timezone.now() - user.otp_created_at
        if otp_age > timedelta(minutes=OTP_EXPIRY_MINUTES):
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response(
                {'message': 'OTP has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify OTP
        if user.otp != otp:
            return Response(
                {'message': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP verified - clear it
        user.otp = None
        user.otp_created_at = None
        user.save()

        # Update session
        update_auth_session(session_id, {'step': 'otp_verified'})

        # Determine next step
        if session_data['user_exists']:
            next_step = 'enter_password'
        else:
            next_step = 'complete_registration'

        return Response({
            'session_id': session_id,
            'user_exists': session_data['user_exists'],
            'message': 'OTP verified successfully',
            'next_step': next_step
        }, status=status.HTTP_200_OK)


class CompleteRegistrationView(APIView):
    """Step 3 (new users only): Complete registration form"""

    def post(self, request):
        from .serializers import CompleteRegistrationSerializer

        serializer = CompleteRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        session_id = serializer.validated_data['session_id']

        # Get session
        session_data = get_auth_session(session_id)
        if not session_data:
            return Response(
                {'message': 'Invalid or expired session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate session state
        if session_data.get('step') != 'otp_verified':
            return Response(
                {'message': 'Please verify OTP first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if session_data.get('user_exists'):
            return Response(
                {'message': 'Invalid flow for existing user'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store registration data in session
        registration_data = {
            'username': serializer.validated_data['username'],
            'password': serializer.validated_data['password'],
            'phone': serializer.validated_data['phone'],
            'first_name': serializer.validated_data.get('first_name', ''),
            'last_name': serializer.validated_data.get('last_name', ''),
        }

        update_auth_session(session_id, {
            'step': 'registration_completed',
            'registration_data': registration_data
        })

        return Response({
            'session_id': session_id,
            'message': 'Registration data saved. Please confirm your password.',
            'next_step': 'confirm_password'
        }, status=status.HTTP_200_OK)


class AuthenticatePasswordView(APIView):
    """Step 4: Authenticate with password (works for both new and existing users)"""
    throttle_classes = [UserAuthThrottle]

    @transaction.atomic
    def post(self, request):
        from .serializers import AuthenticatePasswordSerializer

        serializer = AuthenticatePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        session_id = serializer.validated_data['session_id']
        password = serializer.validated_data['password']

        # Get session
        session_data = get_auth_session(session_id)
        if not session_data:
            return Response(
                {'message': 'Invalid or expired session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if session_data['user_exists']:
            # Existing user - verify password
            if session_data.get('step') != 'otp_verified':
                return Response(
                    {'message': 'Please verify OTP first'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.get(id=session_data['user_id'])

            # Check account lockout
            if user.lockout_until and timezone.now() < user.lockout_until:
                remaining_time = (user.lockout_until - timezone.now()).seconds
                return Response(
                    {'message': f'Account locked. Try again in {remaining_time} seconds.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Verify password
            if not user.check_password(password):
                user.faild_attempts += 1

                if user.faild_attempts >= 5:
                    user.lockout_until = timezone.now() + timedelta(minutes=5)
                    user.faild_attempts = 0
                    user.save()
                    return Response(
                        {'message': 'Too many failed attempts. Account locked for 5 minutes.'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                user.save()
                return Response(
                    {'message': 'Invalid password'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Success - reset failed attempts
            user.faild_attempts = 0
            user.lockout_until = None
            user.is_verified = True  # Mark as verified (2FA complete)
            user.save()

        else:
            # New user - create account
            if session_data.get('step') != 'registration_completed':
                return Response(
                    {'message': 'Please complete registration first'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            registration_data = session_data.get('registration_data')

            # Verify password matches
            if password != registration_data['password']:
                return Response(
                    {'message': 'Password does not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the temporary user and update it with real data
            try:
                user = User.objects.get(id=session_data['user_id'])
                # Update temporary user with real data
                user.username = registration_data['username']
                user.phone = registration_data['phone']
                user.first_name = registration_data['first_name']
                user.last_name = registration_data['last_name']
                user.set_password(registration_data['password'])
                user.is_verified = True

                if user.role == 'admin':
                    user.is_superuser = True
                    user.is_staff = True

                user.save()
            except User.DoesNotExist:
                # Create new user (fallback)
                user = User.objects.create(
                    email=session_data['email'],
                    username=registration_data['username'],
                    phone=registration_data['phone'],
                    first_name=registration_data['first_name'],
                    last_name=registration_data['last_name'],
                    role=session_data['role'],
                    is_verified=True
                )
                user.set_password(registration_data['password'])

                if session_data['role'] == 'admin':
                    user.is_superuser = True
                    user.is_staff = True

                user.save()

            # Send welcome email
            send_welcome_email(user)

        # Create token
        token = create_auth_token(user)
        user_data = get_user_response_data(user)

        # Clear session
        clear_auth_session(session_id)

        return Response({
            'token': token.key,
            'user': user_data,
            'message': 'Authentication successful'
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """Utility: Resend OTP for current session"""

    def post(self, request):
        session_id = request.data.get('session_id')

        session_data = get_auth_session(session_id)
        if not session_data:
            return Response(
                {'message': 'Invalid or expired session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user
        try:
            user = User.objects.get(id=session_data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate and send new OTP
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_otp_email(session_data['email'], otp)

        return Response({
            'message': 'New OTP sent to your email'
        }, status=status.HTTP_200_OK)
