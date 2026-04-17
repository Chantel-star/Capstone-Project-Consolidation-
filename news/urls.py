from django.urls import path
from .views import (
    approve_article,
    home,
    editor_dashboard,
    register,
    create_article,
    update_article,
    ArticleAPIView,
)

urlpatterns = [
    path('', home, name='home'),
    path('approve/<int:article_id>/', approve_article, name='approve_article'),
    path('editor/', editor_dashboard, name='editor_dashboard'),
    path('register/', register, name='register'),
    path('create/', create_article, name='create_article'),
    path('update/<int:article_id>/', update_article, name='update_article'),
    path('api/articles/', ArticleAPIView.as_view(), name='api_articles'),
]