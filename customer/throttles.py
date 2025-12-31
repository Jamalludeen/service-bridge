from rest_framework.throttling import UserRateThrottle

class CustomerProfileThrottle(UserRateThrottle):
    rate = "10/min"