from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('verified', 'google_id', 'profile_picture', 'bio', 'date_of_birth', 'last_login_ip', 'role')}),
    )
    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        (None, {'fields': ('verified', 'google_id', 'profile_picture', 'bio', 'date_of_birth', 'last_login_ip', 'role')}),
    )

    list_display = ('email', 'full_name', 'is_staff', 'is_active', 'role', 'verified')
    search_fields = ('email', 'full_name')
    ordering = ('email',)


