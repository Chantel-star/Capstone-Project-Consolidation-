from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Article, Newsletter, CustomUser, Publisher
from .forms import ArticleForm, RegisterForm, NewsletterForm, PublisherForm
from .serializers import ArticleSerializer


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
"""Display approved articles and newsletters."""
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
            .filter(
                Q(publisher_id__in=publisher_ids)
                | Q(author_id__in=journalist_ids)
            )
            .distinct()
        )

        newsletters = (
            Newsletter.objects.filter(approved=True)
            .filter(
                Q(publisher_id__in=publisher_ids)
                | Q(author_id__in=journalist_ids)
            )
            .distinct()
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
# EDITOR DASHBOARD
# =========================
@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
     """Display pending content for editors."""
    
    publishers = Publisher.objects.filter(editors=request.user)

    pending_articles = Article.objects.filter(
        approved=False,
        publisher__in=publishers,
    )

    pending_independent_articles = Article.objects.filter(
        approved=False,
        publisher__isnull=True,
    )

    pending_newsletters = Newsletter.objects.filter(
        approved=False,
        publisher__in=publishers,
    )

    pending_independent_newsletters = Newsletter.objects.filter(
        approved=False,
        publisher__isnull=True,
    )

    pending_articles = pending_articles | pending_independent_articles
    pending_newsletters = pending_newsletters | pending_independent_newsletters

    return render(
        request,
        "news/editor_dashboard.html",
        {
            "pending_articles": pending_articles.distinct(),
            "pending_newsletters": pending_newsletters.distinct(),
        },
    )


# =========================
# CREATE ARTICLE
# =========================
@login_required
def create_article(request):
     """Allow journalists to create articles."""
    if request.user.role != "journalist":
        messages.error(request, "Only journalists can create articles.")
        return redirect("home")

    if request.method == "POST":
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False

            if not form.cleaned_data.get("publisher"):
                article.publisher = None

            article.save()

            messages.success(
                request,
                "Article submitted for editor approval.",
            )
            return redirect("home")
    else:
        form = ArticleForm()

    return render(
        request,
        "news/create_article.html",
        {"form": form},
    )


# =========================
# APPROVE ARTICLE
# =========================
@require_POST
@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    article.approved = True
    article.save()

    publisher_subscribers = []

    if article.publisher:
        publisher_subscribers = (
            CustomUser.objects.filter(
                subscribed_publishers=article.publisher
            )
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
     """Update an existing article."""
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
            updated_article.approved = False

            if not form.cleaned_data.get("publisher"):
                updated_article.publisher = None

            updated_article.save()

            messages.success(
                request,
                "Article updated and sent for re-approval.",
            )
            return redirect("home")
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "news/update_article.html",
        {"form": form},
    )

# =========================
# DELETE ARTICLE
# =========================
@login_required
def delete_article(request, article_id):
     """Delete an article."""
    
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.author and request.user.role != "editor":
        messages.error(
            request,
            "You do not have permission to delete this article.",
        )
        return redirect("home")

    if request.method == "POST":
        article.delete()

        messages.success(
            request,
            "Article deleted successfully.",
        )
        return redirect("journalist_profile")

    return render(
        request,
        "news/delete_article.html",
        {"article": article},
    )


# =========================
# UPDATE NEWSLETTER
# =========================
@login_required
def update_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id,
    )

    if (
        request.user != newsletter.author
        and request.user.role != "editor"
    ):
        messages.error(
            request,
            "You do not have permission to edit this newsletter.",
        )
        return redirect("home")

    if request.method == "POST":
        form = NewsletterForm(
            request.POST,
            instance=newsletter,
        )

        if form.is_valid():
            updated_newsletter = form.save(commit=False)
            updated_newsletter.author = newsletter.author
            updated_newsletter.approved = False

            if not form.cleaned_data.get("publisher"):
                updated_newsletter.publisher = None

            updated_newsletter.save()

            messages.success(
                request,
                "Newsletter updated and sent for re-approval.",
            )
            return redirect("home")
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "news/update_newsletter.html",
        {"form": form},
    )


# =========================
# DELETE NEWSLETTER
# =========================
@login_required
def delete_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id,
    )

    if (
        request.user != newsletter.author
        and request.user.role != "editor"
    ):
        messages.error(
            request,
            "You do not have permission to delete this newsletter.",
        )
        return redirect("home")

    if request.method == "POST":
        newsletter.delete()

        messages.success(
            request,
            "Newsletter deleted successfully.",
        )
        return redirect("journalist_profile")

    return render(
        request,
        "news/delete_newsletter.html",
        {"newsletter": newsletter},
    )

# =========================
# CREATE NEWSLETTER
# =========================
@login_required
def create_newsletter(request):
    if request.user.role != "journalist":
        messages.error(request, "Only journalists can create newsletters.")
        return redirect("home")

    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.approved = False

            if not form.cleaned_data.get("publisher"):
                newsletter.publisher = None

            newsletter.save()

            messages.success(
                request,
                "Newsletter submitted for editor approval.",
            )
            return redirect("home")
    else:
        form = NewsletterForm()

    return render(
        request,
        "news/create_newsletter.html",
        {"form": form},
    )


# =========================
# APPROVE NEWSLETTER
# =========================
@require_POST
@login_required
@user_passes_test(is_editor)
def approve_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    newsletter.approved = True
    newsletter.save()

    messages.success(request, "Newsletter approved.")
    return redirect("editor_dashboard")


# =========================
# CREATE PUBLISHER
# =========================
@login_required
def create_publisher(request):
    if request.user.role != "editor":
        messages.error(request, "Only editors can create publishers.")
        return redirect("home")

    if request.method == "POST":
        form = PublisherForm(request.POST)

        if form.is_valid():
            publisher = form.save()
            publisher.editors.add(request.user)

            messages.success(request, "Publisher created successfully.")
            return redirect("home")
    else:
        form = PublisherForm()

    return render(
        request,
        "news/create_publisher.html",
        {"form": form},
    )


# =========================
# JOURNALIST PROFILE
# =========================
@login_required
@user_passes_test(is_journalist)
def journalist_profile(request):
    approved_articles = Article.objects.filter(
        author=request.user,
        approved=True,
    )

    pending_articles = Article.objects.filter(
        author=request.user,
        approved=False,
    )

    approved_newsletters = Newsletter.objects.filter(
        author=request.user,
        approved=True,
    )

    pending_newsletters = Newsletter.objects.filter(
        author=request.user,
        approved=False,
    )

    return render(
        request,
        "news/journalist_profile.html",
        {
            "approved_articles": approved_articles,
            "pending_articles": pending_articles,
            "approved_newsletters": approved_newsletters,
            "pending_newsletters": pending_newsletters,
        },
    )


# =========================
# SUBSCRIPTIONS
# =========================
@login_required
@user_passes_test(is_reader)
def manage_subscriptions(request):
     """Manage user subscriptions."""
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role="journalist")

    if request.method == "POST":
        request.user.subscribed_publishers.set(
            Publisher.objects.filter(
                id__in=request.POST.getlist("publishers")
            )
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


# =========================
# REGISTER
# =========================
def register(request):
     """Register a new user account."""
    
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data.get("role")
            user.save()

            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "news/register.html",
        {"form": form},
    )


# =========================
# LOGOUT USER
# =========================
@require_POST
@login_required
def logout_user(request):
    logout(request)
    return redirect("login")


# =========================
# API VIEW
# =========================
class ArticleAPIView(APIView):
     """API view for listing approved articles."""
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

            articles = (
                articles.filter(
                    Q(publisher_id__in=publisher_ids)
                    | Q(author_id__in=journalist_ids)
                )
                .distinct()
            )

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)