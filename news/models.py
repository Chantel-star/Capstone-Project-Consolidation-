from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# ROLE CHOICES
# =========================
ROLE_CHOICES = [
    ("reader", "reader"),
    ("journalist", "Journalist"),
    ("publisher", "Publisher"),
]

role = models.CharField(
    max_length=20,
    choices=ROLE_CHOICES,
    default="reader",
)

# =========================
# CUSTOM USER MODEL
# =========================
class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="reader")

    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='subscribers'
    )

    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='journalist_subscribers'
    )


# =========================
# PUBLISHER MODEL
# =========================

class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# =========================
# ARTICLE MODEL
# =========================

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    approved = models.BooleanField(default=False)

    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='articles')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='articles')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# NEWSLETTER MODEL
# =========================

class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='newsletters')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title