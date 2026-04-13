from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# CUSTOM USER MODEL
# =========================
class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


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
# SUBSCRIPTIONS
# =========================
class PublisherSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} -> {self.publisher.name}"


class JournalistSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='journalist_subscribers'
    )

    def __str__(self):
        return f"{self.user.username} -> {self.journalist.username}"