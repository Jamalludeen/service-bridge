from django.contrib import admin
from .models import Professional, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):

    @admin.display(description="Username")
    def username(self, obj):
        return obj.user.username
    
    list_display = (
        "id",
        "username",
        "city",
        "verification_status",
        "is_active",
        "created_at",
    )

    list_filter = (
        "verification_status",
        "city",
        "preferred_language",
        "is_active",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
        "city",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "avg_rating",
        "total_reviews",
    )

    filter_horizontal = ("services",)


