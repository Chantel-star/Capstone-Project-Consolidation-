from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.core.mail import send_mail
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Article, Newsletter, CustomUser, Publisher
from .forms import ArticleForm, RegisterForm
from .serializers import ArticleSerializer


# =========================
# ROLE CHECKS
# =========================
def is_reader(user):
    return user.is_authenticated and user.role == 'reader'


def is_journalist(user):
    return user.is_authenticated and user.role == 'journalist'


def is_publisher(user):
    return user.is_authenticated and user.role == 'publisher'


# =========================
# CREATE GROUPS
# =========================
def create_groups():
    groups = ['Reader', 'Journalist', 'Publisher']
    for group in groups:
        Group.objects.get_or_create(name=group)


# =========================
# HOME VIEW
# =========================
def home(request):
    articles = Article.objects.filter(approved=True)
    newsletters = Newsletter.objects.none()

    if request.user.is_authenticated:
        newsletters = Newsletter.objects.filter(
            publisher__in=request.user.subscribed_publishers.all()
        )

    return render(request, 'news/home.html', {
        'articles': articles,
        'newsletters': newsletters,
    })


# =========================
# DASHBOARD (PUBLISHER)
# =========================
@login_required
@user_passes_test(is_publisher)
def editor_dashboard(request):
    articles = Article.objects.filter(approved=False)
    return render(request, 'news/editor_dashboard.html', {'articles': articles})


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
            article.author = request.user

            if not article.publisher:
                publisher = Publisher.objects.first()
                if publisher:
                    article.publisher = publisher

            article.save()
            messages.success(request, 'Article created successfully.')
            return redirect('home')
    else:
        form = ArticleForm()

    return render(request, 'news/create_article.html', {'form': form})


# =========================
# APPROVE ARTICLE
# =========================
@login_required
@user_passes_test(is_publisher)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    article.approved = True
    article.save()

    subscribers = CustomUser.objects.filter(
        subscribed_publishers=article.publisher
    ).values_list('email', flat=True)

    send_mail(
        subject='New Article Published',
        message=f'{article.title} is now live!',
        from_email='admin@newsapp.com',
        recipient_list=list(subscribers),
        fail_silently=True,
    )

    try:
        requests.post(
            'https://api.twitter.com/2/tweets',
            headers={'Authorization': 'Bearer YOUR_ACCESS_TOKEN'},
            json={'text': f'New article: {article.title}'},
        )
    except Exception:
        pass

    messages.success(request, 'Article approved.')
    return redirect('editor_dashboard')


# =========================
# UPDATE ARTICLE
# =========================
@login_required
def update_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.user != article.author and request.user.role != 'publisher':
        messages.error(request, 'You do not have permission to edit this article.')
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            updated_article.author = article.author
            updated_article.publisher = updated_article.publisher or article.publisher
            updated_article.approved = False
            updated_article.save()
            messages.success(request, 'Article updated and sent for re-approval.')
            return redirect('home')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'news/update_article.html', {'form': form})


# =========================
# LOGOUT USER
# =========================
def logout_user(request):
    logout(request)
    return redirect('login')

# =========================
# REGISTER
# =========================
def register(request):
    create_groups()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()

            group = Group.objects.filter(name=user.role.capitalize()).first()
            if group:
                user.groups.add(group)

            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'news/register.html', {'form': form})


# =========================
# API VIEW
# =========================
class ArticleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        articles = Article.objects.filter(approved=True)
        user = request.user

        if user.role == 'reader':
            publisher_ids = user.subscribed_publishers.values_list('id', flat=True)
            journalist_ids = user.subscribed_journalists.values_list('id', flat=True)

            articles = articles.filter(
                Q(publisher_id__in=publisher_ids) |
                Q(author_id__in=journalist_ids)
            ).distinct()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


# =========================
# CREATE NEWSLETTER
# =========================
@login_required
def create_newsletter(request):
    if request.user.role not in ['journalist', 'publisher']:
        return redirect('home')

    if request.method == 'POST':
        publisher = Publisher.objects.first()

        Newsletter.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            publisher=publisher,
        )
        messages.success(request, 'Newsletter created successfully.')
        return redirect('home')

    return render(request, 'news/create_newsletter.html')


# =========================
# SUBSCRIPTIONS
# =========================
@login_required
@user_passes_test(is_reader)
def manage_subscriptions(request):
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role='journalist')

    if request.method == 'POST':
        request.user.subscribed_publishers.set(
            Publisher.objects.filter(id__in=request.POST.getlist('publishers'))
        )

        request.user.subscribed_journalists.set(
            CustomUser.objects.filter(
                id__in=request.POST.getlist('journalists'),
                role='journalist',
            )
        )

        messages.success(request, 'Subscriptions updated successfully.')
        return redirect('home')

    return render(request, 'news/subscriptions.html', {
        'publishers': publishers,
        'journalists': journalists,
    })