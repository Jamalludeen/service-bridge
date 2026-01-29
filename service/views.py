from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q


from django.db import transaction

from core.utils.location import bounding_box, haversine_distance
from .permissions import IsProfessionalOwnerOrIsAdmin, IsAdminUserOrProfessionalOwner
from .serializers import AdminServiceSerializer, ProfessionalServiceSerializer
from .filters import ServiceFilter
from .models import Service

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    # permission_classes = [IsProfessionalOwnerOrIsAdmin, IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['title', 'category__name']
    ordering_fields = ["title", "category__name", "price_per_unit"]


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsProfessionalOwnerOrIsAdmin()]

    def get_serializer_class(self):
        user = self.request.user

        if user.is_authenticated and user.role == "admin":
            return AdminServiceSerializer

        return ProfessionalServiceSerializer


    def get_queryset(self):
        user = self.request.user

        queryset = Service.objects.select_related(
            "professional",
            "professional__user",
            "category"
        )

        # Public users (AllowAny)
        if not user.is_authenticated:
            return queryset.filter(is_active=True)

        if user.is_staff or user.role == "admin":
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
    
    @action(detail=False, methods=["GET"])
    def search(self, request):
        queryset = self.get_queryset()
        query = request.query_params.get("q", '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(category__name__icontains=query) |
                Q(description__icontains=query)
            )

        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__id=category)
        
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if min_price:
            queryset = queryset.filter(price_per_unit__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_unit__lte=max_price)
        
        min_rating = request.query_params.get("min_rating")
        if min_rating:
            queryset = queryset.filter(professional__avg_rating__gte=min_rating)
        
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = float(request.query_params.get("radius", 10)) # default 10km

        result = []

        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)

                min_lat, max_lat, min_lng, max_lng = bounding_box(user_lat, user_lng, radius)
        
                queryset = queryset.filter(
                    professional__latitude__gte=min_lat,
                    professional__latitude__lte=max_lat,
                    professional__longitude__gte=min_lng,
                    professional__longitude__lte=max_lng,
                ).exclude(
                    professional__latitude__isnull=True,
                ).exclude(
                    professional__longitude__isnull=True,
                )

                for service in queryset:
                    prof_lat = float(service.professional.latitude)
                    prof_lng = float(service.professional.longitude)
                    distance = haversine_distance(user_lat, user_lng, prof_lat, prof_lng)

                    if distance <= radius:
                        result.append({
                            'service': service,
                            'distance_km': distance,
                        })
            except ValueError:
                return Response(
                    {"message": "Invalid latitude or longitude"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            result = [{'service': service, 'distance_km': None} for service in queryset]
        
        