from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import CustomerProfileSerializer, CustomerUpdateProfileSerializer
from .permissions import IsCustomerOwner
from .models import CustomerProfile
from .throttles import CustomerProfileThrottle

User = get_user_model()


# this view handles requests send by customer to his/her profile
class CustomerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomerProfileThrottle]

    # if the user sends a get request to just return his/her profile data
    def get(self,request):
        self.check_permissions(request)
        profile = get_object_or_404(CustomerProfile, user=request.user)
        serializer = CustomerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # if a post request is send by users we handle profile creation for them
    def post(self, request):
        if request.user.role  == "admin" or request.user.role == "professional":
            return Response(
                {"message": "Your account cannot be switched to a customer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CustomerProfileSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                {
                    "message": "Profile successfully created!",
                    "profile": CustomerProfileSerializer(profile).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    