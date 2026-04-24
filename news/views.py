from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.core.mail import send_mail
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Article, Newsletter, CustomUser, Publisher
from .forms import ArticleForm, RegisterForm
from .serializers import ArticleSerializer
from django.views.decorators.http import require_POST


# =========================
# ROLE CHECKS
# =========================
def is_reader(user):
    return user.is_authenticated and user.role == "reader"


def is_journalist(user):
    return user.is_authenticated and user.role == "journalist"


def is_editor(user):
    return user.is_authenticated and user.role == "editor"


# =========================
# CREATE GROUPS
# =========================
def create_groups():
    groups = ["Reader", "Editor", "Journalist"]
    for group in groups:
        Group.objects.get_or_create(name=group)


# =========================
# HOME VIEW
# =========================
@login_required
def home(request):
    articles = Article.objects.filter(approved=True)
    newsletters = Newsletter.objects.filter(approved=True)

    if request.user.role == "reader":
        publisher_ids = request.user.subscribed_publishers.values_list(
            "id",
            flat=True,
        )
        journalist_ids = request.user.subscribed_journalists.values_list(
            "id",
            flat=True,
        )

        articles = (
            Article.objects.filter(approved=True)
            .filter(Q(publisher_id__in=publisher_ids) | Q(author_id__in=journalist_ids))
            .distinct()
        )

        newsletters = Newsletter.objects.filter(
            approved=True,
            publisher_id__in=publisher_ids,
        )

    return render(
        request,
        "news/home.html",
        {
            "articles": articles,
            "newsletters": newsletters,
        },
    )


# =========================
# DASHBOARD (EDITOR)
# =========================
@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    publisher = getattr(request.user, "managed_publisher", None)

    if not publisher:
        messages.error(request, "No publisher is linked to this editor.")
        return redirect("home")

    articles = Article.objects.filter(
        approved=False,
        publisher=publisher,
    )
    newsletters = Newsletter.objects.filter(
        approved=False,
        publisher=publisher,
    )

    return render(
        request,
        "news/editor_dashboard.html",
        {
            "articles": articles,
            "newsletters": newsletters,
            "publisher": publisher,
        },
    )


# =========================
# CREATE ARTICLE
# =========================
@login_required
def create_article(request):
    """Allow journalists to create articles linked to a publisher."""

    if request.user.role != "journalist":
        return redirect("home")

    if request.method == "POST":
        form = ArticleForm(request.POST)

        if form.is_valid():
            publisher = Publisher.objects.filter(
                journalists=request.user
            ).first()

            if not publisher:
                publisher = Publisher.objects.first()

            if not publisher:
                messages.error(request, "No publisher exists yet.")
                return redirect("home")

            article = form.save(commit=False)
            article.author = request.user
            article.publisher = publisher
            article.save()
            form.save_m2m()

            messages.success(request, "Article created successfully.")
            return redirect("home")
    else:
        form = ArticleForm()

    return render(request, "create_article.html", {"form": form})

# =========================
# APPROVE ARTICLE
# =========================
@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    publisher = getattr(request.user, "managed_publisher", None)

    if not publisher:
        messages.error(request, "No publisher is linked to this editor.")
        return redirect("home")

    article = get_object_or_404(
        Article,
        id=article_id,
        publisher=publisher,
    )

    article.approved = True
    article.save()

    publisher_subscribers = []
    if article.publisher:
        publisher_subscribers = (
            CustomUser.objects.filter(subscribed_publishers=article.publisher)
            .exclude(email="")
            .values_list("email", flat=True)
        )

    journalist_subscribers = (
        CustomUser.objects.filter(subscribed_journalists=article.author)
        .exclude(email="")
        .values_list("email", flat=True)
    )

    subscribers = set(publisher_subscribers) | set(journalist_subscribers)

    if subscribers:
        send_mail(
            subject="New Article Published",
            message=f"{article.title} is now live!",
            from_email="admin@newsapp.com",
            recipient_list=list(subscribers),
            fail_silently=True,
        )

    try:
        requests.post(
            "https://api.twitter.com/2/tweets",
            headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"},
            json={"text": f"New article: {article.title}"},
            timeout=5,
        )
    except Exception:
        pass

    messages.success(request, "Article approved.")
    return redirect("editor_dashboard")


# =========================
# UPDATE ARTICLE
# =========================
@login_required
def update_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.author and request.user.role != "editor":
        messages.error(
            request,
            "You do not have permission to edit this article.",
        )
        return redirect("home")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            updated_article.author = article.author
            updated_article.publisher = updated_article.publisher or article.publisher
            updated_article.approved = False
            updated_article.save()
            messages.success(
                request,
                "Article updated and sent for re-approval.",
            )
            return redirect("home")
    else:
        form = ArticleForm(instance=article)

    return render(request, "news/update_article.html", {"form": form})


# =========================
# LOGOUT USER
# =========================
@require_POST
@login_required
def logout_user(request):
    logout(request)
    return redirect("login")


# =========================
# REGISTER
# =========================
def register(request):
    create_groups()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data["role"]
            user.save()

            group = Group.objects.filter(name=user.role.capitalize()).first()
            if group:
                user.groups.add(group)

            if user.role == "editor":
                Publisher.objects.create(
                    name=f"{user.username}'s Publisher",
                    editor=user,
                )

            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "news/register.html", {"form": form})


# =========================
# API VIEW
# =========================
class ArticleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        articles = Article.objects.filter(approved=True)

        if user.role == "reader":
            publisher_ids = user.subscribed_publishers.values_list(
                "id",
                flat=True,
            )
            journalist_ids = user.subscribed_journalists.values_list(
                "id",
                flat=True,
            )

            articles = articles.filter(
                Q(publisher_id__in=publisher_ids) | Q(author_id__in=journalist_ids)
            ).distinct()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


# =========================
# CREATE NEWSLETTER
# =========================
@login_required
def create_newsletter(request):
    if request.user.role != "journalist":
        messages.error(
            request,
            "You do not have permission to create a newsletter.",
        )
        return redirect("home")

    if request.method == "POST":
        publisher = Publisher.objects.first()

        if not publisher:
            messages.error(request, "No publisher exists yet.")
            return redirect("home")

        Newsletter.objects.create(
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            author=request.user,
            publisher=publisher,
            approved=False,
        )
        messages.success(
            request,
            "Newsletter created and sent for approval.",
        )
        return redirect("home")

    return render(request, "news/create_newsletter.html")


# ========================
# APPROVE_NEWSLETTER
# =========================
@login_required
@user_passes_test(is_editor)
def approve_newsletter(request, newsletter_id):
    publisher = getattr(request.user, "managed_publisher", None)

    if not publisher:
        messages.error(request, "No publisher is linked to this editor.")
        return redirect("home")

    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id,
        publisher=publisher,
    )

    newsletter.approved = True
    newsletter.save()

    messages.success(request, "Newsletter approved.")
    return redirect("editor_dashboard")


# =========================
# SUBSCRIPTIONS
# =========================
@login_required
@user_passes_test(is_reader)
def manage_subscriptions(request):
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role="journalist")

    if request.method == "POST":
        request.user.subscribed_publishers.set(
            Publisher.objects.filter(id__in=request.POST.getlist("publishers"))
        )

        request.user.subscribed_journalists.set(
            CustomUser.objects.filter(
                id__in=request.POST.getlist("journalists"),
                role="journalist",
            )
        )

        messages.success(request, "Subscriptions updated successfully.")
        return redirect("home")

    return render(
        request,
        "news/subscriptions.html",
        {
            "publishers": publishers,
            "journalists": journalists,
        },
    )
