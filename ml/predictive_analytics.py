
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