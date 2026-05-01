from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Newsletter, Publisher


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "role",
        ]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "publisher",
        ]


class NewsletterForm(forms.ModelForm):
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        empty_label="Select a publisher",
        required=True,
    )

    class Meta:
        model = Newsletter
        fields = [
            "title",
            "content",
            "publisher",
        ]


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = [
            "name",
            "editors",
            "journalists",
        ]