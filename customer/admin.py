from django.contrib import admin
from .models import CustomerProfile, Cart, CartItem

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'city', 'profile_image']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_item', 'total_price', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'service', 'quantity', 'estimated_price', 'added_at']
    readonly_fields = ['added_at', 'updated_at']


