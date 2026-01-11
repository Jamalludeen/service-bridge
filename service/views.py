from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .serializers import ServiceSerializer
from .models import Service
from .permissions import IsProfessionalOwnerOrIsAdmin


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsProfessionalOwnerOrIsAdmin]

    def get_queryset(self):
        return self.queryset.filter(is_active=True)
