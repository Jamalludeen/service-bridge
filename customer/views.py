from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .serializers import CustomerProfileSerializer
from .models import CustomerProfile


class CustomerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if CustomerProfile.objects.filter(user=request.user).exists():
            return Response({"message": "Customer with profile already exists!!!"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data

        serializer = CustomerProfileSerializer(data=data)
        if serializer.is_valid():
            profile = serializer.save()

            profile_serializer = CustomerProfileSerializer(profile)

            return Response(
                {"message": "Profile successfully created!", "profile":profile_serializer.data},
                status=status.HTTP_201_CREATED
                )
        
        return Response(
           serializer.errors,
           status=status.HTTP_400_BAD_REQUEST
        )
    