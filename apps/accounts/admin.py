from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_staff"]
    list_filter = [*BaseUserAdmin.list_filter, "role"]
    fieldsets = [*BaseUserAdmin.fieldsets, ("Vai trò", {"fields": ["role"]})]
    add_fieldsets = [*BaseUserAdmin.add_fieldsets, ("Vai trò", {"fields": ["role"]})]
