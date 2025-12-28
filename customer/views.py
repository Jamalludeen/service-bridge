from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import RetrieveAPIView

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import CustomerProfileSerializer, CustomerRetrieveProfileSerializer, CustomerUpdateProfileSerializer
from .permissions import IsCustomerOwner, IsAdmin
from .models import CustomerProfile

User = get_user_model()


# this view handles requests send by customer to his/her profile
class CustomerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # if the user sends a get request to just return his/her profile data
    def get(self,request):
        self.check_permissions(request)
        profile = CustomerProfile.objects.get(user=request.user)
        print("profile: ", profile)
        serializer = CustomerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # if a post request is send by users we handle profile creation for them
    def post(self, request):
        user = get_object_or_404(User, username=request.user)

        # if the user is already associated with a profile
        if CustomerProfile.objects.filter(user=user).exists():
            return Response(
                {"message": "Customer with profile already exist!"}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        data = request.data.copy()
        user_id = user.id
        data["user"] = user_id

        serializer = CustomerProfileSerializer(data=data)
        # check for data validation
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
    
    def patch(self, request, *args, **kwargs):
        # set the premission, so only the creator of profile can update
        self.permission_classes = [IsCustomerOwner]
        user_id = request.user.id
        profile = get_object_or_404(CustomerProfile, user=user_id)
        
        self.check_object_permissions(request, profile)

        serializer = CustomerUpdateProfileSerializer(instance=profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile successfully updated!", "data": serializer.data}, 
                status=status.HTTP_200_OK
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request):
        # set the premission, so only the creator of profile can delete
        self.permission_classes = [IsCustomerOwner]
        self.check_permissions(request)

        user = self.request.user
        profile = get_object_or_404(CustomerProfile, user=user)
        profile.delete()
        return Response(
            {"message": "Profile deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    