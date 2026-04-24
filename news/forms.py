from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Newsletter


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content"]


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["title", "content"]
