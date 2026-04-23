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
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="reader",
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

    def __str__(self):
        return self.username


# =========================
# PUBLISHER MODEL
# =========================
class Publisher(models.Model):
    name = models.CharField(max_length=255)
    editor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_publisher",
        limit_choices_to={"role": "editor"},
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
        on_delete=models.CASCADE,
        related_name="articles",
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# NEWSLETTER MODEL
# =========================
class Newsletter(models.Model):
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
        on_delete=models.CASCADE,
        related_name="newsletters",
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title