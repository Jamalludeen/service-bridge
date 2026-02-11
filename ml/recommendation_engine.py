from django.db.models import Count, Avg, Q, F
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import math

from service.models import Service
from professional.models import Professional, ServiceCategory
from booking.models import Booking
from customer.models import CustomerProfile
from .models import UserInteraction, ServiceSimilarity, CustomerPreference



class RecommendationEngine:
    """
    Multi-strategy recommendation engine for Service-Bridge.

    Strategies:
    1. Collaborative Filtering - "Users who booked X also booked Y"
    2. Content-Based - Similar services based on category, price
    3. Popularity-Based - Trending/popular services
    4. Location-Based - Services near the customer
    5. Hybrid - Combination of above strategies
    """

    def __init__(self, customer_profile):
        self.customer = customer_profile
        self.user = customer_profile.user

    def get_recommended_services(self, limit=10):
        """
        Get personalized service recommendations for the customer.
        Uses a hybrid approach combining multiple strategies.
        """
        scores = {}

        # Strategy 1: Collaborative filtering (40% weight)
        collab_services = self._collaborative_filtering_services()
        for service_id, score in collab_services.items():
            scores[service_id] = scores.get(service_id, 0) + (score * 0.4)

        # Strategy 2: Content-based from booking history (30% weight)
        content_services = self._content_based_services()
        for service_id, score in content_services.items():
            scores[service_id] = scores.get(service_id, 0) + (score * 0.3)

        # Strategy 3: Location-based (20% weight)
        location_services = self._location_based_services()
        for service_id, score in location_services.items():
            scores[service_id] = scores.get(service_id, 0) + (score * 0.2)

        # Strategy 4: Popularity/trending (10% weight)
        popular_services = self._popularity_based_services()
        for service_id, score in popular_services.items():
            scores[service_id] = scores.get(service_id, 0) + (score * 0.1)

        # Remove already booked services
        booked_service_ids = Booking.objects.filter(
            customer=self.customer
        ).values_list('service_id', flat=True)

        for service_id in booked_service_ids:
            scores.pop(service_id, None)

        # Sort by score and return top N
        sorted_services = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        service_ids = [s[0] for s in sorted_services]

        # Fetch services preserving order
        services = Service.objects.filter(
            id__in=service_ids,
            is_active=True,
            professional__is_active=True,
            professional__verification_status='VERIFIED'
        ).select_related('professional__user', 'category')

        # Preserve recommendation order
        service_dict = {s.id: s for s in services}
        return [service_dict[sid] for sid in service_ids if sid in service_dict]
    
    def _collaborative_filtering_services(self):
        """
        Find services booked by users with similar booking patterns.
        "Customers who booked X also booked Y"
        """
        scores = {}

        # Get categories the customer has booked
        customer_categories = Booking.objects.filter(
            customer=self.customer,
            status='COMPLETED'
        ).values_list('service__category_id', flat=True).distinct()

        if not customer_categories:
            return scores

        # Find other customers who booked same categories
        similar_customers = CustomerProfile.objects.filter(
            bookings__service__category_id__in=customer_categories,
            bookings__status='COMPLETED'
        ).exclude(id=self.customer.id).distinct()[:100]

        # Get services those customers booked
        similar_bookings = Booking.objects.filter(
            customer__in=similar_customers,
            status='COMPLETED'
        ).exclude(
            service__category_id__in=customer_categories
        ).values('service_id').annotate(
            count=Count('id')
        ).order_by('-count')[:50]

        max_count = similar_bookings[0]['count'] if similar_bookings else 1

        for booking in similar_bookings:
            # Normalize score to 0-1
            scores[booking['service_id']] = booking['count'] / max_count

        return scores
    
    def _content_based_services(self):
        """
        Recommend services similar to what customer has booked.
        Based on category, price range, professional rating.
        """
        scores = {}

        # Get customer's booking history
        past_bookings = Booking.objects.filter(
            customer=self.customer,
            status='COMPLETED'
        ).select_related('service', 'service__category')

        if not past_bookings:
            return scores

        # Calculate customer's preferences
        booked_categories = set()
        avg_price = Decimal('0')
        total_price = Decimal('0')

        for booking in past_bookings:
            booked_categories.add(booking.service.category_id)
            total_price += booking.estimated_price

        avg_price = total_price / len(past_bookings) if past_bookings else Decimal('0')
        price_tolerance = avg_price * Decimal('0.5')  # 50% tolerance

        # Find similar services
        similar_services = Service.objects.filter(
            is_active=True,
            professional__is_active=True,
            professional__verification_status='VERIFIED'
        ).exclude(
            bookings__customer=self.customer
        )

        for service in similar_services:
            score = 0.0

            # Category match (high weight)
            if service.category_id in booked_categories:
                score += 0.5

            # Price similarity
            price_diff = abs(service.price_per_unit - avg_price)
            if price_diff <= price_tolerance:
                price_score = 1 - (float(price_diff) / float(price_tolerance))
                score += 0.3 * price_score

            # Professional rating boost
            if service.professional.avg_rating:
                rating_score = service.professional.avg_rating / 5.0
                score += 0.2 * rating_score

            if score > 0:
                scores[service.id] = score

        return scores
    
    def _location_based_services(self):
        """
        Recommend services from professionals near the customer.
        """
        scores = {}

        if not self.customer.latitude or not self.customer.longitude:
            return scores

        customer_lat = float(self.customer.latitude)
        customer_lon = float(self.customer.longitude)

        # Get nearby professionals (within ~50km)
        professionals = Professional.objects.filter(
            is_active=True,
            verification_status='VERIFIED',
            latitude__isnull=False,
            longitude__isnull=False
        )

        for professional in professionals:
            distance = self._haversine_distance(
                customer_lat, customer_lon,
                float(professional.latitude), float(professional.longitude)
            )

            # Score inversely proportional to distance (max 50km)
            if distance <= 50:
                distance_score = 1 - (distance / 50)

                # Get services from this professional
                for service in professional.services_offered.filter(is_active=True):
                    scores[service.id] = max(
                        scores.get(service.id, 0),
                        distance_score
                    )

        return scores
    
    def _popularity_based_services(self):
        """
        Recommend trending/popular services based on recent bookings.
        """
        from django.utils import timezone
        from datetime import timedelta

        scores = {}

        # Get services with most bookings in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        popular = Booking.objects.filter(
            created_at__gte=thirty_days_ago,
            status__in=['COMPLETED', 'ACCEPTED', 'IN_PROGRESS']
        ).values('service_id').annotate(
            booking_count=Count('id'),
            avg_rating=Avg('professional__avg_rating')
        ).order_by('-booking_count')[:50]

        max_count = popular[0]['booking_count'] if popular else 1

        for item in popular:
            # Combine booking count and rating
            count_score = item['booking_count'] / max_count
            rating_score = (item['avg_rating'] or 3.0) / 5.0
            scores[item['service_id']] = (count_score * 0.7) + (rating_score * 0.3)

        return scores
    
    # PROFESSIONAL RECOMMENDATIONS

    def get_recommended_professionals(self, category_id=None, limit=10):
        """
        Get recommended professionals for the customer.
        Optionally filter by category.
        """
        scores = {}

        queryset = Professional.objects.filter(
            is_active=True,
            verification_status='VERIFIED'
        )

        if category_id:
            queryset = queryset.filter(services__id=category_id)

        queryset = queryset.select_related('user').prefetch_related('services')

        for professional in queryset:
            score = self._calculate_professional_score(professional)
            scores[professional.id] = score

        # Sort by score
        sorted_professionals = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        professional_ids = [p[0] for p in sorted_professionals]

        # Fetch and preserve order
        professional_dict = {p.id: p for p in queryset.filter(id__in=professional_ids)}
        return [professional_dict[pid] for pid in professional_ids if pid in professional_dict]
    
    def _calculate_professional_score(self, professional):
        """
        Calculate a composite score for a professional.
        """
        score = 0.0

        # Rating component (30%)
        if professional.avg_rating:
            score += (professional.avg_rating / 5.0) * 0.3

        # Experience component (15%)
        exp_years = professional.years_of_experience or 0
        exp_score = min(exp_years / 10, 1.0)  # Cap at 10 years
        score += exp_score * 0.15

        # Review count component (15%)
        reviews = professional.total_reviews or 0
        review_score = min(reviews / 50, 1.0)  # Cap at 50 reviews
        score += review_score * 0.15

        # Completion rate component (25%)
        total_bookings = Booking.objects.filter(professional=professional).count()
        completed_bookings = Booking.objects.filter(
            professional=professional,
            status='COMPLETED'
        ).count()

        if total_bookings > 0:
            completion_rate = completed_bookings / total_bookings
            score += completion_rate * 0.25

        # Location proximity component (15%)
        if self.customer.latitude and professional.latitude:
            distance = self._haversine_distance(
                float(self.customer.latitude), float(self.customer.longitude),
                float(professional.latitude), float(professional.longitude)
            )
            if distance <= 50:
                distance_score = 1 - (distance / 50)
                score += distance_score * 0.15

        return score
    
    # "SIMILAR SERVICES" RECOMMENDATIONS

    def get_similar_services(self, service_id, limit=5):
        """
        Get services similar to a given service.
        Useful for "You may also like" sections.
        """
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return []

        scores = {}

        # Same category services
        same_category = Service.objects.filter(
            category=service.category,
            is_active=True,
            professional__is_active=True,
            professional__verification_status='VERIFIED'
        ).exclude(id=service_id)

        for similar in same_category:
            score = 0.5  # Base score for same category

            # Price similarity
            price_diff = abs(similar.price_per_unit - service.price_per_unit)
            max_price = max(similar.price_per_unit, service.price_per_unit)
            if max_price > 0:
                price_similarity = 1 - (float(price_diff) / float(max_price))
                score += price_similarity * 0.3

            # Professional rating
            if similar.professional.avg_rating:
                score += (similar.professional.avg_rating / 5.0) * 0.2

            scores[similar.id] = score

        # Sort and return
        sorted_services = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        service_ids = [s[0] for s in sorted_services]
        services = Service.objects.filter(id__in=service_ids).select_related(
            'professional__user', 'category'
        )

        service_dict = {s.id: s for s in services}
        return [service_dict[sid] for sid in service_ids if sid in service_dict]
    
    # CATEGORY RECOMMENDATIONS
    def get_recommended_categories(self, limit=5):
        """
        Recommend service categories the customer might be interested in.
        """
        scores = {}

        # Get customer's booked categories
        booked_categories = set(
            Booking.objects.filter(
                customer=self.customer
            ).values_list('service__category_id', flat=True)
        )

        # All categories except booked ones
        all_categories = ServiceCategory.objects.exclude(id__in=booked_categories)

        # Find categories often booked together
        for booked_cat_id in booked_categories:
            # Customers who booked this category also booked...
            co_booked = Booking.objects.filter(
                customer__bookings__service__category_id=booked_cat_id,
                status='COMPLETED'
            ).exclude(
                service__category_id=booked_cat_id
            ).values('service__category_id').annotate(
                count=Count('id')
            ).order_by('-count')[:10]

            for item in co_booked:
                cat_id = item['service__category_id']
                if cat_id not in booked_categories:
                    scores[cat_id] = scores.get(cat_id, 0) + item['count']

        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        for cat_id in scores:
            scores[cat_id] = scores[cat_id] / max_score

        # Sort and return
        sorted_categories = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        category_ids = [c[0] for c in sorted_categories]
        categories = ServiceCategory.objects.filter(id__in=category_ids)

        cat_dict = {c.id: c for c in categories}
        return [cat_dict[cid] for cid in category_ids if cid in cat_dict]

    # UTILITY METHODS

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points in kilometers.
        """
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
    
class ProfessionalRecommendationEngine:
    """
    Recommendations for professionals.
    """

    def __init__(self, professional):
        self.professional = professional

    def get_suggested_categories(self, limit=3):
        """
        Suggest service categories the professional might want to add.
        Based on what similar professionals offer.
        """
        # Current categories
        current_categories = set(self.professional.services.values_list('id', flat=True))

        # Find professionals with similar existing categories
        similar_professionals = Professional.objects.filter(
            services__in=current_categories,
            is_active=True,
            verification_status='VERIFIED'
        ).exclude(id=self.professional.id).distinct()

        # Get categories those professionals have that this one doesn't
        suggested = ServiceCategory.objects.filter(
            professionals__in=similar_professionals
        ).exclude(
            id__in=current_categories
        ).annotate(
            count=Count('professionals')
        ).order_by('-count')[:limit]

        return list(suggested)
    
    def get_optimal_pricing(self, service_id):
        """
        Suggest optimal pricing based on market data.
        """
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return None

        # Get similar services in same category
        similar_services = Service.objects.filter(
            category=service.category,
            is_active=True,
            professional__is_active=True,
            professional__verification_status='VERIFIED'
        ).exclude(id=service_id)

        if not similar_services:
            return None

        # Calculate market stats
        prices = list(similar_services.values_list('price_per_unit', flat=True))
        avg_price = sum(prices) / len(prices)

        # Adjust based on professional's rating
        rating_adjustment = 1.0
        if self.professional.avg_rating:
            # Higher rating = can charge more
            rating_adjustment = 0.9 + (self.professional.avg_rating / 50)  # 0.9 to 1.1

        # Adjust based on experience
        exp_adjustment = 1.0
        if self.professional.years_of_experience:
            exp_adjustment = 1.0 + (self.professional.years_of_experience * 0.02)  # +2% per year

        suggested_price = float(avg_price) * rating_adjustment * exp_adjustment

        return {
            'current_price': float(service.price_per_unit),
            'market_average': float(avg_price),
            'suggested_price': round(suggested_price, 2),
            'min_market': float(min(prices)),
            'max_market': float(max(prices)),
        }