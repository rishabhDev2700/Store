from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .forms import UserCreationForm

from accounts.models import User


# Register your models here.
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(User, CustomUserAdmin)
