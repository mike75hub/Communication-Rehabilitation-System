from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'department', 'is_active_officer', 'is_staff')
    list_filter = ('user_type', 'is_active_officer', 'is_staff', 'is_superuser', 'department')
    fieldsets = UserAdmin.fieldsets + (
        ('Professional Information', {
            'fields': ('user_type', 'phone', 'department', 'badge_number', 'profile_picture', 'is_active_officer')
        }),
    )
    list_editable = ('is_active_officer',)  # Allow quick editing of officer status
    
    def get_queryset(self, request):
        # Show all users in admin
        return super().get_queryset(request)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date')