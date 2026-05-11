"""
URL configuration for the News Project application.

This module connects URL paths to views.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("news.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]