from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[
    ('admin', 'Admin'),
    ('publisher', 'Publisher'),
    ('journalist', 'Journalist'),
    ('subscriber', 'Subscriber'),
])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']