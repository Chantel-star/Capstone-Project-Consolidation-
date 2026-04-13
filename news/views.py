from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Article, PublisherSubscription, JournalistSubscription
from .forms import ArticleForm, RegisterForm
from .serializers import ArticleSerializer


# =========================
# ROLE CHECKS
# =========================
def is_reader(user):
    return user.is_authenticated and user.role == 'reader'


def is_journalist(user):
    return user.is_authenticated and user.role == 'journalist'


def is_editor(user):
    return user.is_authenticated and user.role == 'editor'


# =========================
# CREATE GROUPS
# =========================
def create_groups():
    groups = ['Reader', 'Editor', 'Journalist']
    for group in groups:
        Group.objects.get_or_create(name=group)


# =========================
# HOME VIEW
# =========================
def home(request):
    articles = Article.objects.filter(approved=True)
    return render(request, 'news/home.html', {'articles': articles})


# =========================
# EDITOR DASHBOARD
# =========================
@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    articles = Article.objects.filter(approved=False)
    return render(request, 'news/editor_dashboard.html', {'articles': articles})


# =========================
# CREATE ARTICLE (JOURNALIST)
# =========================
@login_required
@user_passes_test(is_journalist)
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            return redirect('home')

    else:
        form = ArticleForm()

    return render(request, 'news/create_article.html', {'form': form})


# =========================
# APPROVE ARTICLE (EDITOR)
# =========================
@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # Approve article
    article.approved = True
    article.save()

    # Get subscribers
    publisher_subscribers = PublisherSubscription.objects.filter(
        publisher=article.publisher
    ).values_list('user', flat=True)

    journalist_subscribers = JournalistSubscription.objects.filter(
        journalist=article.author
    ).values_list('user', flat=True)

    # Combine subscribers
    subscribers = set(publisher_subscribers) | set(journalist_subscribers)

    # Simulate notification
    for user_id in subscribers:
        print(f"Notify user {user_id}: New article '{article.title}'")

    messages.info(request, "Notifications sent to subscribers.")
    return redirect('editor_dashboard')


# =========================
# UPDATE ARTICLE
# =========================
@login_required
def update_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.author and request.user.role != 'editor':
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            updated_article = form.save(commit=False)
            updated_article.author = article.author
            updated_article.approved = False
            updated_article.save()
            return redirect('home')

    else:
        form = ArticleForm(instance=article)

    return render(request, 'news/update_article.html', {'form': form})


# =========================
# REGISTER
# =========================
def register(request):
    create_groups()

    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data['role']

            user.role = role
            user.save()

            group = Group.objects.get(name=role.capitalize())
            user.groups.add(group)

            login(request, user)
            return redirect('home')

    return render(request, 'news/register.html', {'form': form})


# =========================
# API: SUBSCRIBED ARTICLES
# =========================
class ArticleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        articles = Article.objects.filter(approved=True)

        # If reader → apply subscription filtering
        if user.role == 'reader':

            publisher_ids = PublisherSubscription.objects.filter(
                user=user
            ).values_list('publisher_id', flat=True)

            journalist_ids = JournalistSubscription.objects.filter(
                user=user
            ).values_list('journalist_id', flat=True)

            articles = articles.filter(
                Q(publisher_id__in=publisher_ids) |
                Q(author_id__in=journalist_ids)
            ).distinct()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)