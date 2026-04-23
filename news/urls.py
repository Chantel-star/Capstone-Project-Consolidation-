from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home,
    register,
    create_article,
    create_newsletter,
    update_article,
    editor_dashboard,
    approve_article,
    approve_newsletter,
    logout_user,
    ArticleAPIView,
    manage_subscriptions,
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="news/login.html"),
        name="login",
    ),
    path("logout/", logout_user, name="logout"),

    path("create/", create_article, name="create_article"),
    path(
        "newsletters/create/",
        create_newsletter,
        name="create_newsletter",
    ),
    path(
        "update/<int:article_id>/",
        update_article,
        name="update_article",
    ),

    path("editor/", editor_dashboard, name="editor_dashboard"),
    path(
        "approve/<int:article_id>/",
        approve_article,
        name="approve_article",
    ),
    path(
        "approve-newsletter/<int:newsletter_id>/",
        approve_newsletter,
        name="approve_newsletter",
    ),

    path("subscriptions/", manage_subscriptions, name="subscriptions"),
    path("api/articles/", ArticleAPIView.as_view(), name="api_articles"),
]