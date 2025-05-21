from django.contrib.auth.forms import (
    UserCreationForm as CreationForm,
    UserChangeForm as ChangeForm,
)
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm as UChangeForm,
    UserCreationForm as UCreationForm,
)
from django import forms

from accounts.models import User


class AdminUserCreationForm(UCreationForm):
    username = None
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]


class AdminUserChangeForm(UChangeForm):
    username = None

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class UserCreationForm(CreationForm):
    username = None
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "border-2 border-neutral-400 bg-gray-100 p-2"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "border-2 border-neutral-400 bg-gray-100 p-2"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "border-2 border-neutral-400 bg-gray-100 p-2"}
            ),
        }


class UserChangeForm(ChangeForm):
    username = None

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
