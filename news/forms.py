from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class RegisterForm(UserCreationForm):
    """Form for registering new users."""
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
    """Form for creating and updating articles."""
    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "publisher",
        ]


class NewsletterForm(forms.ModelForm):
    """Form for creating and updating newsletters."""
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        empty_label="Independent",
        required=False,
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
        fields = ["name", "editors", "journalists"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["editors"].queryset = CustomUser.objects.filter(
            role="editor"
        )

        self.fields["journalists"].queryset = CustomUser.objects.filter(
            role="journalist"
        )