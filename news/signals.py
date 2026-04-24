from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Article


def create_groups():
    """Create user groups and assign article permissions."""

    article_content_type = ContentType.objects.get_for_model(Article)

    view_article = Permission.objects.get(
        codename="view_article",
        content_type=article_content_type,
    )
    add_article = Permission.objects.get(
        codename="add_article",
        content_type=article_content_type,
    )
    change_article = Permission.objects.get(
        codename="change_article",
        content_type=article_content_type,
    )
    delete_article = Permission.objects.get(
        codename="delete_article",
        content_type=article_content_type,
    )

    reader_group, _ = Group.objects.get_or_create(name="Reader")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    publisher_group, _ = Group.objects.get_or_create(name="Publisher")

    reader_group.permissions.set([view_article])

    journalist_group.permissions.set([
        view_article,
        add_article,
        change_article,
    ])

    editor_group.permissions.set([
        view_article,
        change_article,
        delete_article,
    ])

    publisher_group.permissions.set([
        view_article,
        add_article,
        change_article,
        delete_article,
    ])