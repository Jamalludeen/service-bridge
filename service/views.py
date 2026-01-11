from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .serializers import AdminServiceSerializer, ProfessionalServiceSerializer
from .models import Service
from .permissions import IsProfessionalOwnerOrIsAdmin


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated, IsProfessionalOwnerOrIsAdmin]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        user = self.request.user

        if user.is_staff or user.role == "admin":
            return AdminServiceSerializer

        return ProfessionalServiceSerializer

    def get_queryset(self):
        return self.queryset.filter(is_active=True)
