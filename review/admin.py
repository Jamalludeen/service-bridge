from django.contrib import admin

from .models import Review, ReviewResponse


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'booking', 'professional', 'customer', 'rating',
		'is_approved', 'is_flagged', 'created_at'
	)
	list_filter = ('is_approved', 'is_flagged', 'rating', 'created_at')
	search_fields = ('customer__username', 'professional__user__username', 'comment', 'booking__id')
	raw_id_fields = ('booking', 'customer', 'professional')
	readonly_fields = ('created_at', 'updated_at')
	ordering = ('-created_at',)

	actions = ['approve_reviews', 'flag_reviews', 'unflag_reviews']

	def approve_reviews(self, request, queryset):
		updated = queryset.update(is_approved=True, is_flagged=False, flag_reason='')
		self.message_user(request, f"{updated} review(s) approved.")
	approve_reviews.short_description = 'Approve selected reviews'

	def flag_reviews(self, request, queryset):
		updated = queryset.update(is_flagged=True)
		self.message_user(request, f"{updated} review(s) flagged.")
	flag_reviews.short_description = 'Flag selected reviews'

	def unflag_reviews(self, request, queryset):
		updated = queryset.update(is_flagged=False, flag_reason='')
		self.message_user(request, f"{updated} review(s) unflagged.")
	unflag_reviews.short_description = 'Unflag selected reviews'


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
	list_display = ('id', 'review', 'professional', 'created_at')
	search_fields = ('professional__user__username', 'response_text', 'review__id')
	raw_id_fields = ('review', 'professional')
	readonly_fields = ('created_at', 'updated_at')
	ordering = ('-created_at',)
