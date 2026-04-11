from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Article, PublisherSubscription, JournalistSubscription
from .forms import ArticleForm
from .serializers import ArticleSerializer

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# =========================
# ROLE CHECKS
# =========================
def is_journalist(user):
    return user.role == 'journalist'


def is_editor(user):
    return user.role == 'editor'


# =========================
# HOME VIEW
# =========================
def home(request):
    articles = Article.objects.filter(approved=True)
    return render(request, 'news/home.html', {'articles': articles})


# =========================
# EDITOR DASHBOARD
# =========================
@user_passes_test(is_editor)
def editor_dashboard(request):
    articles = Article.objects.filter(approved=False)
    return render(request, 'news/editor_dashboard.html', {'articles': articles})


# =========================
# APPROVE ARTICLE
# =========================
@user_passes_test(is_editor)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()
    return redirect('home')


# =========================
# UPDATE ARTICLE
# =========================
@login_required
@user_passes_test(is_journalist)
def update_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # Allow editor OR author
    if request.user != article.author and request.user.role != 'editor':
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            updated_article = form.save(commit=False)

            # Keep original author
            updated_article.author = article.author

            # Reset approval after edit
            updated_article.approved = False

            updated_article.save()
            return redirect('home')

    else:
        form = ArticleForm(instance=article)

    return render(request, 'news/update_article.html', {'form': form})


# =========================
# API VIEW
# =========================
class SubscribedArticlesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        publisher_ids = PublisherSubscription.objects.filter(
            user=user
        ).values_list('publisher_id', flat=True)

        journalist_ids = JournalistSubscription.objects.filter(
            user=user
        ).values_list('journalist_id', flat=True)

        # ONLY approved articles
        articles = Article.objects.filter(approved=True)

        articles = articles.filter(
            Q(publisher_id__in=publisher_ids) |
            Q(author_id__in=journalist_ids)
        ).distinct()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

# =========================
# REGISTER
# =========================

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    else:
        form = UserCreationForm()

    return render(request, 'news/register.html', {'form': form})


# =========================
# CREATE ARTICLE
# =========================
@login_required
@user_passes_test(is_journalist)
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)

            # Assign current user as author
            article.author = request.user

            # New articles must be approved
            article.approved = False

            article.save()
            return redirect('home')

    else:
        form = ArticleForm()

    return render(request, 'news/create_article.html', {'form': form})