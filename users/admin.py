from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_recruiter', 'is_candidate')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)