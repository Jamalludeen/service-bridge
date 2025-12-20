from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import RetrieveAPIView

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import CustomerProfileSerializer, CustomerRetrieveProfileSerializer, CustomerUpdateProfileSerializer
from .permissions import IsCustomerOwner
from .models import CustomerProfile

User = get_user_model()



class CustomerProfileUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsCustomerOwner]

    def patch(self, request, *args, **kwargs):
        user_id = request.user.id
        profile = get_object_or_404(CustomerProfile, user=user_id)
        
        self.check_object_permissions(request, profile)

        serializer = CustomerUpdateProfileSerializer(instance=profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CustomerProfileRetrieveView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsCustomerOwner]
    serializer_class = CustomerRetrieveProfileSerializer

    def get_object(self):
        return get_object_or_404(CustomerProfile, user=self.request.user)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        return super().get(request, *args, **kwargs)



class CustomerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, username=request.user)

        if CustomerProfile.objects.filter(user=user).exists():
            return Response(
                {"message": "Customer with profile already exist!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        data = request.data.copy()
        user_id = user.id
        data["user"] = user_id

        serializer = CustomerProfileSerializer(data=data)
        if serializer.is_valid():
            profile = serializer.save()

            profile_serializer = CustomerProfileSerializer(profile)

            return Response(
                {"message": "Profile successfully created!", "profile": profile_serializer.data},
                status=status.HTTP_201_CREATED
                )
        
        return Response(
           serializer.errors,
           status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request):
        self.permission_classes = [IsCustomerOwner]
        self.check_permissions(request)

        user = self.request.user
        profile = get_object_or_404(CustomerProfile, user=user)
        profile.delete()
        return Response(
            {"message": "Profile deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    