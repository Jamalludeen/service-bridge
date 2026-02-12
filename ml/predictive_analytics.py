
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from booking.models import Booking
from professional.models import Professional


class CancellationRiskPredictor:
    """
    Predict the likelihood of a booking being cancelled.
    Uses historical patterns and booking characteristics.
    """

    def predict_risk(self, booking):
        """
        Calculate cancellation risk score (0.0 to 1.0).
        Higher score = higher risk of cancellation.
        """
        risk_factors = []

        # Factor 1: Customer's historical cancellation rate
        customer_cancellation_rate = self._get_customer_cancellation_rate(
            booking.customer
        )
        risk_factors.append(('customer_history', customer_cancellation_rate, 0.25))

        # Factor 2: Professional's rejection/cancellation rate
        professional_issue_rate = self._get_professional_issue_rate(
            booking.professional
        )
        risk_factors.append(('professional_history', professional_issue_rate, 0.20))

        # Factor 3: Booking lead time (very short or very long = higher risk)
        lead_time_risk = self._calculate_lead_time_risk(booking)
        risk_factors.append(('lead_time', lead_time_risk, 0.15))

        # Factor 4: Price deviation from customer's average
        price_risk = self._calculate_price_risk(booking)
        risk_factors.append(('price_deviation', price_risk, 0.15))

        # Factor 5: First-time customer-professional pairing
        is_first_time = self._is_first_time_pairing(booking)
        risk_factors.append(('first_time', 0.3 if is_first_time else 0.0, 0.10))

        # Factor 6: Category cancellation rate
        category_risk = self._get_category_cancellation_rate(
            booking.service.category_id
        )
        risk_factors.append(('category_rate', category_risk, 0.15))

        # Calculate weighted risk score
        total_risk = sum(score * weight for _, score, weight in risk_factors)

        return {
            'risk_score': round(total_risk, 3),
            'risk_level': self._get_risk_level(total_risk),
            'factors': {name: round(score, 3) for name, score, _ in risk_factors}
        }
    
    def _get_customer_cancellation_rate(self, customer):
        """Customer's historical cancellation rate."""
        bookings = Booking.objects.filter(customer=customer)
        total = bookings.count()

        if total < 3:  # Not enough history
            return 0.2  # Assume moderate risk

        cancelled = bookings.filter(
            status='CANCELLED',
            cancelled_by=customer.user
        ).count()

        return cancelled / total

    def _get_professional_issue_rate(self, professional):
            """Professional's rejection + cancellation rate."""
            bookings = Booking.objects.filter(professional=professional)
            total = bookings.count()

            if total < 5:
                return 0.15

            issues = bookings.filter(
                Q(status='REJECTED') |
                Q(status='CANCELLED', cancelled_by=professional.user)
            ).count()

            return issues / total
    
    def _calculate_lead_time_risk(self, booking):
        """Risk based on booking lead time."""
        now = timezone.now().date()
        days_until = (booking.scheduled_date - now).days

        if days_until < 1:  # Same day - higher risk
            return 0.4
        elif days_until < 3:
            return 0.2
        elif days_until > 30:  # Very far out
            return 0.3
        else:
            return 0.1
        
    def _calculate_price_risk(self, booking):
        """Risk based on price deviation from customer norm."""
        customer_avg = Booking.objects.filter(
            customer=booking.customer,
            status='COMPLETED'
        ).aggregate(avg=Avg('estimated_price'))['avg']

        if not customer_avg:
            return 0.1

        deviation = abs(float(booking.estimated_price) - float(customer_avg))
        deviation_pct = deviation / float(customer_avg)

        # High deviation = higher risk
        if deviation_pct > 1.0:  # More than 100% different
            return 0.4
        elif deviation_pct > 0.5:
            return 0.3
        else:
            return 0.1
        
    def _is_first_time_pairing(self, booking):
        """Check if customer and professional have worked together before."""
        previous = Booking.objects.filter(
            customer=booking.customer,
            professional=booking.professional,
            status='COMPLETED'
        ).exists()

        return not previous

    def _get_category_cancellation_rate(self, category_id):
        """Cancellation rate for this service category."""
        bookings = Booking.objects.filter(service__category_id=category_id)
        total = bookings.count()

        if total < 10:
            return 0.15

        cancelled = bookings.filter(status='CANCELLED').count()
        return cancelled / total
    
    def _get_risk_level(self, score):
        """Convert score to human-readable level."""
        if score < 0.2:
            return 'LOW'
        elif score < 0.4:
            return 'MODERATE'
        elif score < 0.6:
            return 'HIGH'
        else:
            return 'VERY_HIGH'


class DemandForecaster:
    """
    Forecast service demand by category, location, and time.
    """

    def get_demand_forecast(self, category_id=None, city=None, days_ahead=7):
        """
        Forecast demand for the next N days.
        """
        forecasts = []

        for day_offset in range(days_ahead):
            target_date = timezone.now().date() + timedelta(days=day_offset)

            # Get historical data for this day of week
            historical = self._get_historical_demand(
                target_date.weekday(),
                category_id,
                city
            )

            forecasts.append({
                'date': target_date.isoformat(),
                'day_of_week': target_date.strftime('%A'),
                'predicted_bookings': historical['avg_bookings'],
                'confidence': historical['confidence'],
                'trend': historical['trend']
            })

        return forecasts
    
    def _get_historical_demand(self, day_of_week, category_id=None, city=None):
        """
        Analyze historical demand for a specific day of week.
        """
        # Look at last 12 weeks
        lookback = timezone.now() - timedelta(weeks=12)

        queryset = Booking.objects.filter(
            created_at__gte=lookback,
            scheduled_date__week_day=day_of_week + 2  # Django week_day: 1=Sunday
        )

        if category_id:
            queryset = queryset.filter(service__category_id=category_id)

        if city:
            queryset = queryset.filter(city__icontains=city)

        # Group by week
        weekly_counts = []
        for week in range(12):
            week_start = timezone.now() - timedelta(weeks=12-week)
            week_end = week_start + timedelta(weeks=1)

            count = queryset.filter(
                created_at__gte=week_start,
                created_at__lt=week_end
            ).count()
            weekly_counts.append(count)

        if not weekly_counts or sum(weekly_counts) == 0:
            return {
                'avg_bookings': 0,
                'confidence': 'LOW',
                'trend': 'STABLE'
            }

        avg_bookings = sum(weekly_counts) / len(weekly_counts)

        # Calculate trend (comparing recent vs older)
        recent_avg = sum(weekly_counts[-4:]) / 4 if len(weekly_counts) >= 4 else avg_bookings
        older_avg = sum(weekly_counts[:4]) / 4 if len(weekly_counts) >= 4 else avg_bookings

        if recent_avg > older_avg * 1.2:
            trend = 'INCREASING'
        elif recent_avg < older_avg * 0.8:
            trend = 'DECREASING'
        else:
            trend = 'STABLE'

        # Confidence based on data volume
        total_bookings = sum(weekly_counts)
        if total_bookings > 50:
            confidence = 'HIGH'
        elif total_bookings > 20:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'

        return {
            'avg_bookings': round(avg_bookings, 1),
            'confidence': confidence,
            'trend': trend
        }