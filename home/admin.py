from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TreeSubmission

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

@admin.register(TreeSubmission)
class TreeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('tree_name', 'location', 'description')