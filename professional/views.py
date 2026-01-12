from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .serializers import ServiceCategorySerializer, ProfessionalCreateSerializer, ProfessionalUpdateSerializer, ProfessionalRetrieveSerializer
from .models import ServiceCategory, Professional
from .permissions import IsProfessionalOwner
from .throttles import ProfessionalProfileThrottle

User = get_user_model()



class ProfessionalProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # throttle_classes = [ProfessionalProfileThrottle]

    def get_permissions(self):
        """
        Enforce permissions BEFORE request handling
        """
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsProfessionalOwner()]
        return [IsAuthenticated()]

    def get(self, request):
        """
        - Professional → can see only own profile
        - Admin → can see all profiles (read-only)
        """

        # PROFESSIONAL USER
        if request.user.role == "professional":
            profile = get_object_or_404(Professional, user=request.user)
            self.check_object_permissions(request, profile)

            serializer = ProfessionalRetrieveSerializer(profile)
            return Response(
                {"data": serializer.data},
                status=status.HTTP_200_OK
            )

        # ADMIN USER
        if request.user.role == "admin":
            professionals = Professional.objects.all()
            serializer = ProfessionalRetrieveSerializer(professionals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "You are not allowed to access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    def post(self, request):
        """
        Create professional profile (once per user)
        """

        user = request.user

        if user.role == "customer":
            return Response (
                {"message": "You are not allowed to access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Must be verified
        if not user.is_verified:
            return Response(
                {"detail": "Please verify your account first."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prevent duplicate profile
        if Professional.objects.filter(user=user).exists():
            return Response(
                {"detail": "Professional profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProfessionalCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        profile = serializer.save(user=user)

        return Response(
            {
                "message": "Profile successfully created.",
                "profile": ProfessionalCreateSerializer(profile).data,
            },
            status=status.HTTP_201_CREATED
        )

    def patch(self, request):
        """
        Update professional profile (owner only)
        """

        profile = get_object_or_404(Professional, user=request.user)
        self.check_object_permissions(request, profile)

        # Enforce verification
        if not request.user.is_verified:
            return Response(
                {"detail": "Account must be verified to update profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProfessionalUpdateSerializer(
            instance=profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profile successfully updated.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        """
        Delete professional profile (owner only)
        """

        profile = get_object_or_404(Professional, user=request.user)
        self.check_object_permissions(request, profile)

        profile.delete()
        return Response(
            {"message": "Profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
     

class ServiceCategoryViewset(ModelViewSet):
    serializer_class = ServiceCategorySerializer
    queryset = ServiceCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
