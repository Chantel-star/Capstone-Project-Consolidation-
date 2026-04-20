from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ("editor", "Editor"),
        ("journalist", "Journalist"),
        ("publisher", "Publisher"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']