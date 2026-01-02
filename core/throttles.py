from rest_framework.throttling import UserRateThrottle


class UserAuthThrottle(UserRateThrottle):
    rate = "10/min"


class OTPVerifyThrottle(UserRateThrottle):
    rate = "1/min"

