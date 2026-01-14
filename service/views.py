from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .serializers import AdminServiceSerializer, ProfessionalServiceSerializer
from .models import Service
from .permissions import IsProfessionalOwnerOrIsAdmin, IsAdminUserOrProfessionalOwner


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [IsProfessionalOwnerOrIsAdmin, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        user = self.request.user

        if user.is_staff or user.role == "admin":
            return AdminServiceSerializer

        return ProfessionalServiceSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Service.objects.select_related(
            "professional",
            "professional__user",
            "category"
        )

        if user.role == "admin" or user.is_staff:
            return queryset

        if user.role == "professional":
            return queryset.filter(professional__user=user)

        if user.role == "customer":
            return queryset.filter(is_active=True)

        return Service.objects.none()
    
    @action(detail=True, methods=["GET"], permission_classes=[IsAdminUserOrProfessionalOwner])
    def active(self, request, pk=None):
        service = get_object_or_404(Service, pk=pk)
        if service.is_active:
            return Response(
                {"message": "Service is already active"},
                status=status.HTTP_200_OK
            )
        
        service.is_active = True
        service.save()
        return Response(
            {"message": "Service activated"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["GET"], permission_classes=[IsAdminUserOrProfessionalOwner])
    def disable(self, request, pk=None):
        service = get_object_or_404(Service, pk=pk)
        
        if service.is_active:
            service.is_active = False
            service.save()
            return Response(
                {"message": "Service deactivated"},
                status=status.HTTP_200_OK
            )
    
        return Response(
            {"message": "Service is already disables"},
            status=status.HTTP_200_OK
        )
        
        