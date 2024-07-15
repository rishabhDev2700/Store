from django.contrib.auth.forms import UserCreationForm as CreationForm
from django import forms

from accounts.models import User


class UserCreationForm(CreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
