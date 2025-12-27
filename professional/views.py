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
        # check if user is professional
        if request.user.role == 'professional':
            # set the permission class 
            self.permission_classes = [IsProfessionalUser]

            # get the user's profile who has requested
            professional_obj = Professional.objects.get(user=request.user)
            # check for the ownership of the object
            self.check_object_permissions(request, professional_obj)

            serializer = ProfessionalCreateSerializer(professional_obj)
            return Response(
                {"data": serializer.data},
                status=status.HTTP_200_OK
            )
        
        # if the user is admin we show up all the profiles for admin
        if request.user.role == 'admin':
            self.permission_classes = [IsAuthenticated]
            professionals = Professional.objects.all()
            serializer = ProfessionalCreateSerializer(professionals, many=True)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

    def patch(self, request):
        # set the permission, so only the profile owner be able to update his/her profile
        self.permission_classes = [IsProfessionalOwner]
        profile = get_object_or_404(Professional, user=request.user)

        # enforce to check the object permission
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

        # if the user account is not verified
        if not user.is_verified:
            return Response(
                {
                    "message": "Please verify your account!",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        # if the requested user's profile exists, return an error message
        if Professional.objects.filter(user=user).exists():
            return Response(
                {"message": "Professional with profile already exist!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
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
