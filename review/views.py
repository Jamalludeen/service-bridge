from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Count, Q

from .models import Review, ReviewResponse
from .serializers import (
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewDetailSerializer,
    ReviewResponseSerializer,
    ProfessionalReviewStatsSerializer
)
from .permissions import IsReviewOwner, IsProfessionalOfReview
from professional.models import Professional



class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews

    Endpoints:
    - POST   /review/           - Create review (Customer)
    - GET    /review/           - List reviews (filtered by user role)
    - GET    /review/{id}/      - Review detail
    - PUT    /review/{id}/      - Update review (Customer, within 24hrs)
    - DELETE /review/{id}/      - Delete review (Admin only)
    - POST   /review/{id}/respond/  - Professional responds to review
    - GET    /review/professional/{id}/stats/  - Get professional's review stats
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'customer':
            # Customer sees their own reviews
            return Review.objects.filter(
                customer=user,
                is_approved=True
            ).select_related('booking', 'professional__user')

        elif user.role == 'professional':
            # Professional sees reviews for their services
            return Review.objects.filter(
                professional__user=user,
                is_approved=True
            ).select_related('booking', 'customer')

        elif user.role == 'admin':
            # Admin sees all reviews
            return Review.objects.all().select_related(
                'booking', 'customer', 'professional__user'
            )

        return Review.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action == 'list':
            return ReviewListSerializer
        return ReviewDetailSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsReviewOwner()]
        elif self.action == 'respond':
            return [IsAuthenticated(), IsProfessionalOfReview()]
        return [IsAuthenticated()]
