from rest_framework.throttling import UserRateThrottle


class ProfessionalProfileThrottle(UserRateThrottle):
    rate = '10/min'