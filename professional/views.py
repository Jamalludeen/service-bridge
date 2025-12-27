from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .serializers import ServiceCategorySerializer, ProfessionalCreateSerializer, ProfessionalUpdateSerializer
from .models import ServiceCategory, Professional
from .permissions import IsProfessionalUser, IsProfessionalOwner

User = get_user_model()



class CreateProfessionalProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        pass

    def patch(self, request):
        self.permission_classes = [IsProfessionalOwner]
        profile = get_object_or_404(Professional, user=request.user)

        self.check_object_permissions(request, profile)

        serializer = ProfessionalUpdateSerializer(instance=profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile successfully updated!", "data":serializer.data},
                status=status.HTTP_200_OK
            )


    def post(self, request):
        user = get_object_or_404(User, username=request.user.username)

        if Professional.objects.filter(user=user).exists():
            return Response(
                {"message": "Professional with profile already exist!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        if not user.is_verified:
            return Response(
                {
                    "message": "Please verify your account!",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        # data = request.data.dict()
        # data['user'] = user.id

        # print(type(request.data.get("services")), request.data.get("services"))
        # print(request.data.getlist("services"))


        serializer = ProfessionalCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            profile = serializer.save(user=user)


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
