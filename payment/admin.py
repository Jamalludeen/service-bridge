from django.contrib import admin
from .models import Payment, PaymentHistory


class PaymentHistoryInline(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'note', 'created_at']
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'booking', 'amount',
        'payment_method', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'transaction_id', 'external_transaction_id',
        'booking__customer__user__email',
        'booking__professional__user__email'
    ]
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    inlines = [PaymentHistoryInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('booking', 'amount', 'payment_method')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'external_transaction_id', 'status')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['payment', 'from_status', 'to_status', 'changed_by', 'created_at']
    list_filter = ['to_status', 'created_at']
    readonly_fields = ['payment', 'from_status', 'to_status', 'changed_by', 'note', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
