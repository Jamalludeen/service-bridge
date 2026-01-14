from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from django.db import transaction

from .serializers import AdminServiceSerializer, ProfessionalServiceSerializer
from .models import Service
from .permissions import IsProfessionalOwnerOrIsAdmin, IsAdminUserOrProfessionalOwner
from .filters import ServiceFilter

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [IsProfessionalOwnerOrIsAdmin, IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['professional__user__username', 'title', 'category__name']
    ordering_fields = ["title", "category__name", "price_per_unit"]

    def get_serializer_class(self):
        user = self.request.user

        if user.role == "admin":
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
    
    @action(detail=True, methods=["POST"], permission_classes=[IsAdminUserOrProfessionalOwner])
    def active(self, request, pk=None):
        service = self.get_object()

        serializer = self.get_serializer(instance=service)
        if service.is_active:
            return Response(
                {"message": "Service is already active", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        with transaction.atomic():
            service.is_active = True
            service.save()

        serializer = self.get_serializer(instance=service)
        return Response(
            {"message": "Service activated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @action(detail=True, methods=["POST"], permission_classes=[IsAdminUserOrProfessionalOwner])
    def disable(self, request, pk=None):
        service = self.get_object()
        serializer = self.get_serializer(instance=service)

        if not service.is_active:
            return Response(
                {"message": "Service is already disabled", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        with transaction.atomic():
            service.is_active = False
            service.save()

        serializer = self.get_serializer(instance=service)
        return Response(
            {"message": "Service deactivated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
        
        