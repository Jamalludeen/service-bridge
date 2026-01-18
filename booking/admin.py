from django.contrib import admin
from .models import Booking, BookingStatusHistory


class BookingStatusHistoryInline(admin.TabularInline):
    model = BookingStatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'note', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'professional', 'service',
        'status', 'scheduled_date', 'estimated_price', 'created_at'
    ]
    list_filter = ['status', 'scheduled_date', 'city', 'created_at']
    search_fields = [
        'customer__user__email', 'professional__user__email',
        'service__title', 'address'
    ]
    readonly_fields = ['created_at', 'updated_at', 'accepted_at', 'started_at', 'completed_at']
    inlines = [BookingStatusHistoryInline]


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'from_status', 'to_status', 'changed_by', 'created_at']
    list_filter = ['to_status', 'created_at']
    readonly_fields = ['booking', 'from_status', 'to_status', 'changed_by', 'note', 'created_at']
