from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .serializers import ServiceCategorySerializer, ProfessionalCreateSerializer
from .models import ServiceCategory, Professional

User = get_user_model()



class CreateProfessionalProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, username=request.user.username)


        if Professional.objects.filter(user=user).exists():
            return Response(
                {"message": "Professional with profile already exist!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        data = request.data.copy()
        data['user'] = user.id

        serializer = ProfessionalCreateSerializer(data=data)
        if serializer.is_valid():
            profile = serializer.save()

            profile_serializer = ProfessionalCreateSerializer(profile)

            return Response(
                {"message": "Profile successfully created!", "profile": profile_serializer.data},
                status=status.HTTP_201_CREATED
                )
        
        return Response(
           serializer.errors,
           status=status.HTTP_400_BAD_REQUEST
        )



class ServiceCategoryViewset(ModelViewSet):
    serializer_class = ServiceCategorySerializer
    queryset = ServiceCategory.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
