from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email=forms.EmailField(required=False)
    team_name = forms.CharField(required=False, max_length=100)

    class Meta:
        model = User
        fields = ('username', 'team_name', 'email', 'password1', 'password2')