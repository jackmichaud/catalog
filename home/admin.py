from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TreeSubmission, Notification

# register your models here

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# @admin.register(TreeSubmission)
# class TreeSubmissionAdmin(admin.ModelAdmin):
#     list_display = ('tree_name', 'location', 'description')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'message')
    readonly_fields = ('created_at',)