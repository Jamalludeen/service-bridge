import pytest

@pytest.mark.parametrize('from_status,to_status', [
    ('PENDING', 'HELD'),
    ('HELD', 'RELEASED'),
    ('HELD', 'REFUNDED'),
    ('PENDING', 'CANCELLED'),
])
@pytest.mark.django_db
def test_payment_status_transition(from_status, to_status):
    from .factories import PaymentFactory

    payment = PaymentFactory(status=from_status)
    payment.status = to_status
    payment.save()

    payment.refresh_from_db()
    assert payment.status == to_status

