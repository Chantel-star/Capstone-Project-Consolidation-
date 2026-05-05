from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    ArticleAPIView,
    approve_article,
    approve_newsletter,
    create_article,
    create_newsletter,
    create_publisher,
    delete_article,
    delete_newsletter,
    editor_dashboard,
    home,
    journalist_profile,
    logout_user,
    manage_subscriptions,
    register,
    update_article,
    update_newsletter,
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
    path("newsletters/create/", create_newsletter, name="create_newsletter"),

    path("publisher/create/", create_publisher, name="create_publisher"),

    path("update/<int:article_id>/", update_article, name="update_article"),
    path("delete/<int:article_id>/", delete_article, name="delete_article"),

    path(
        "newsletters/update/<int:newsletter_id>/",
        update_newsletter,
        name="update_newsletter",
    ),
    path(
        "newsletters/delete/<int:newsletter_id>/",
        delete_newsletter,
        name="delete_newsletter",
    ),

    path("editor/", editor_dashboard, name="editor_dashboard"),

    path("approve/<int:article_id>/", approve_article, name="approve_article"),
    path(
        "approve-newsletter/<int:newsletter_id>/",
        approve_newsletter,
        name="approve_newsletter",
    ),

    path("subscriptions/", manage_subscriptions, name="subscriptions"),
    path("journalist/", journalist_profile, name="journalist_profile"),

    path("api/articles/", ArticleAPIView.as_view(), name="api_articles"),
]