from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# =========================
# ROLE CHOICES
# =========================
ROLE_CHOICES = [
    ("reader", "Reader"),
    ("journalist", "Journalist"),
    ("editor", "Editor"),
]


# =========================
# CUSTOM USER MODEL
# =========================
class CustomUser(AbstractUser):
     """Custom user model with role support."""
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="reader",
    )

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )

    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        blank=True,
        related_name="subscribers",
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="journalist_subscribers",
    )

    def save(self, *args, **kwargs):
        """Clear reader subscription fields for non-reader users."""

        if self.email:
            self.email = self.email.lower()

        super().save(*args, **kwargs)

        if self.role != "reader":
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def __str__(self):
        """Return the username as the readable user name."""

        return self.username

# =========================
# PUBLISHER MODEL
# =========================
class Publisher(models.Model):
     """Model representing a news article."""
    name = models.CharField(max_length=100)
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="editing_publishers",
        blank=True,
    )
    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="journalist_publishers",
        blank=True,
    )

    def __str__(self):
        return self.name


# =========================
# ARTICLE MODEL
# =========================
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        limit_choices_to={"role": "journalist"},
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the article title."""
        return self.title


# =========================
# NEWSLETTER MODEL
# =========================
class Newsletter(models.Model):
     """Model representing a newsletter post."""
     
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="newsletters",
        limit_choices_to={"role": "journalist"},
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletters",
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title