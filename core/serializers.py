from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'phone', 'role', 'password',
        ]

    def validate_phone(self, phone: str):
        """
        Validate Afghan phone numbers only.
        Accepts:
        - +937XXXXXXXX
        - 07XXXXXXXX
        """

        phone = phone.strip().replace(" ", "")

        # Convert 07xxxxxxxx to +937xxxxxxxx
        if phone.startswith("07"):
            phone = "+93" + phone[1:]

        # Regex for Afghan mobile numbers
        afghan_phone_regex = r'^\+93(70|71|72|73|74|75|76|77|78|79)\d{7}$'

        if not re.match(afghan_phone_regex, phone):
            raise serializers.ValidationError(
                "Phone number must be a valid Afghan number (e.g. +9376XXXXXXX)."
            )

        return phone

    def validate(self, attrs):
        # Password confirmation
        # if attrs['password'] != attrs['password2']:
        #     raise serializers.ValidationError(
        #         {"password": "Passwords do not match."}
        #     )

        # Email validation (simple, exam-safe)
        email: str = attrs.get('email', '')
        if not email.endswith("@gmail.com"):
            raise serializers.ValidationError(
                {"email": "Please enter a valid email address."}
            )

        return attrs

    def create(self, validated_data):
        # validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class InitiateAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        email = email.strip().lower()
        if not email.endswith("@gmail.com"):
            raise serializers.ValidationError("Please enter a valid Gmail address.")
        return email


class VerifyOTPSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=255)
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate_otp(self, otp):
        if not otp.isdigit():
            raise serializers.ValidationError("OTP must be numeric.")
        return otp


class CompleteRegistrationSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    phone = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_phone(self, phone):
        phone = phone.strip().replace(" ", "")
        if phone.startswith("07"):
            phone = "+93" + phone[1:]
        afghan_phone_regex = r'^\+93(70|71|72|73|74|75|76|77|78|79)\d{7}$'
        if not re.match(afghan_phone_regex, phone):
            raise serializers.ValidationError("Phone must be valid Afghan number.")

        # Check uniqueness
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return phone

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already taken.")
        return username


class AuthenticatePasswordSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
