from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('verified', 'google_id', 'profile_picture', 'bio')}),
    )
    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        (None, {'fields': ('verified', 'google_id', 'profile_picture', 'bio')}),
    )

    list_display = ('email', 'full_name', 'verified')
    search_fields = ('email', 'full_name')
    ordering = ('email',)


