from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (
    ServiceCategorySerializer, 
    ProfessionalCreateSerializer, 
    ProfessionalUpdateSerializer, 
    ProfessionalRetrieveSerializer
)
from .models import ServiceCategory, Professional
from .permissions import IsProfessionalOwner
# from .throttles import ProfessionalProfileThrottle

User = get_user_model()


class ProfessionalProfileViewSet(ModelViewSet):
    """
    Professional Profile Management
    """

    queryset = Professional.objects.select_related("user").prefetch_related("services")
    authentication_classes = [TokenAuthentication]

    # -------------------------------
    # Permissions
    # -------------------------------
    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProfessionalOwner()]
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # -------------------------------
    # Serializer selection
    # -------------------------------
    def get_serializer_class(self):
        if self.action == "create":
            return ProfessionalCreateSerializer
        if self.action in ["update", "partial_update"]:
            return ProfessionalUpdateSerializer
        return ProfessionalRetrieveSerializer

    # -------------------------------
    # Queryset control
    # -------------------------------
    def get_queryset(self):
        user = self.request.user

        # Admin → all profiles
        if user.is_authenticated and user.role == "admin":
            return self.queryset

        # Professional → own profile only
        if user.is_authenticated and user.role == "professional":
            return self.queryset.filter(user=user)

        # Public → list only active professionals
        return self.queryset.filter(is_active=True)

    # -------------------------------
    # CREATE
    # -------------------------------
    def create(self, request, *args, **kwargs):
        user = request.user

        if user.role == "customer":
            return Response(
                {"detail": "You are not allowed to create a professional profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_verified:
            return Response(
                {"detail": "Please verify your account first."},
                status=status.HTTP_403_FORBIDDEN
            )

        if Professional.objects.filter(user=user).exists():
            return Response(
                {"detail": "Professional profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save(user=user)

        return Response(
            {
                "message": "Profile successfully created.",
                "data": ProfessionalRetrieveSerializer(profile).data
            },
            status=status.HTTP_201_CREATED
        )

    # -------------------------------
    # UPDATE / PARTIAL UPDATE
    # -------------------------------
    def perform_update(self, serializer):
        user = self.request.user

        if not user.is_verified:
            raise PermissionError("Account must be verified to update profile.")

        serializer.save()

    # -------------------------------
    # DESTROY
    # -------------------------------
    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        self.perform_destroy(profile)
        return Response(
            {"message": "Profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

     

class ServiceCategoryViewset(ModelViewSet):
    serializer_class = ServiceCategorySerializer
    queryset = ServiceCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
