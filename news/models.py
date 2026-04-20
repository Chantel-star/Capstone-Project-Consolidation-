from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# ROLE CHOICES
# =========================
ROLE_CHOICES = [
    ("editor", "Editor"),
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        symmetrical=False,
        blank=True,
        related_name='subscribers'
    )

    subscribed_journalists = models.ManyToManyField(
        'CustomUser',
        symmetrical=False,
        blank=True,
        related_name='journalist_followers'
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

    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# NEWSLETTER MODEL
# =========================

class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title