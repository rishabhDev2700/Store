from dataclasses import fields
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import PasswordChangeForm

from accounts.forms import (
    AdminUserCreationForm,
    AdminUserChangeForm,
    AdminPasswordChangeForm,
)

from accounts.models import User
from unfold.admin import ModelAdmin


# Register your models here.
class CustomUserAdmin(UserAdmin, ModelAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    change_password_form = AdminPasswordChangeForm
    change_password_form = PasswordChangeForm
    list_display = ("email", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Personal Info",
            {
                "fields": ("first_name", "last_name"),
            },
        ),
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    # list_display = ("email", "first_name", "last_name", "is_staff")
    # search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    exclude = ("username", "usable_password")


admin.site.register(User, CustomUserAdmin)
