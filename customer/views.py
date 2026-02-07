from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    CustomerUpdateProfileSerializer, 
    CustomerRetrieveProfileSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    CartItemSerializer,
    CartSerializer,
)
from .permissions import IsCustomerOwner
from .models import CustomerProfile, Cart, CartItem
from booking.models import Booking
# from .throttles import CustomerProfileThrottle

User = get_user_model()


class CartViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes  = [IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_cart(self, customer):
        """Get or create cart for customer"""
        cart, created = Cart.objects.get_or_create(customer=customer)
        return cart
    
    def list(self, request):
        """
        GET /api/cart/
        Retrieve customer's cart with all items
        """
        try:
            customer = request.user.customer_profile
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = self.get_cart(customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def add(self, request):
        try:
            customer = request.user.customer
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            ) 
        
        cart = self.get_cart(customer)

        if cart.total_items >= 50:  # Maximum 50 items per cart
            return Response(
                {"error": "Cart is full. Maximum 50 items allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CartItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            service_id = serializer.validated_data['service'].id

            # Check if service already in cart
            existing_item = CartItem.objects.filter(
                cart=cart,
                service_id=service_id
            ).first()

            if existing_item:
                # Update quantity instead of creating duplicate
                existing_item.quantity += serializer.validated_data.get('quantity', 1)
                existing_item.save()

                item_serializer = CartItemSerializer(existing_item)
                return Response(
                    {
                        "message": "Cart item quantity updated",
                        "item": item_serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            # Create new cart item
            cart_item = serializer.save(cart=cart)
            item_serializer = CartItemSerializer(cart_item)

            return Response(
                {
                    "message": "Item added to cart successfully",
                    "item": item_serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        customer = request.user.customer

        cart = self.get_cart(customer)
        cart_item = self.get_object(CartItem, id=item_id, cart=cart)
        
        serializer = CartItemUpdateSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            item_serializer = CartItemSerializer(cart_item)
            return Response(
                {
                    "message": "Cart item updated successfully",
                    "item": item_serializer.data
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def delete_item(self, request, item_id=None):
        customer = request.user.customer
        cart = self.get_cart(customer=customer)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        service_title = cart_item.service.title
        cart_item.delete()
        return Response(
            {"message": f"{service_title} deleted from cart!"},
            status=status.HTTP_200_OK
        )



# this view handles requests send by customer to his/her profile
class CustomerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # throttle_classes = [CustomerProfileThrottle]

    # if the user sends a get request to just return his/her profile data
    def get(self, request):
        self.check_permissions(request)
        profile = get_object_or_404(CustomerProfile, user=request.user)
        serializer = CustomerRetrieveProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # if a post request is send by users we handle profile creation for them
    # def post(self, request):
    #     if request.user.role  == "admin" or request.user.role == "professional":
    #         return Response(
    #             {"message": "Your account cannot be switched to a customer"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     serializer = CustomerProfileSerializer(
    #         data=request.data,
    #         context={'request': request}
    #     )

    #     if serializer.is_valid():
    #         profile = serializer.save()
    #         return Response(
    #             {
    #                 "message": "Profile successfully created!",
    #                 "profile": CustomerProfileSerializer(profile).data
    #             },
    #             status=status.HTTP_201_CREATED
    #         )

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    