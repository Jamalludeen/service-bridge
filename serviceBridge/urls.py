from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('core.urls')),
    path("customer/", include("customer.urls")),
    path("professional/", include("professional.urls")),
    path("service/", include("service.urls")),
    path('api/booking/', include('booking.urls')),
    path('api/payment/', include('payment.urls')),
    path('review/', include('review.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
