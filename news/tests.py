from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Publisher, Article

User = get_user_model()


class ArticleAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.reader = User.objects.create_user(
            username="reader1",
            email="reader1@test.com",
            password="testpass123",
            role="reader",
        )

        self.editor = User.objects.create_user(
            username="editor1",
            email="editor1@test.com",
            password="testpass123",
            role="editor",
        )

        self.journalist = User.objects.create_user(
            username="journalist1",
            email="journalist1@test.com",
            password="testpass123",
            role="journalist",
        )

        self.other_journalist = User.objects.create_user(
            username="journalist2",
            email="journalist2@test.com",
            password="testpass123",
            role="journalist",
        )

        # Publishers
        self.publisher = Publisher.objects.create(
            name="Subscribed Publisher"
        )

        self.other_publisher = Publisher.objects.create(
            name="Unsubscribed Publisher"
        )

        # Articles
        self.subscribed_article = Article.objects.create(
            title="Subscribed Article",
            content="Visible to reader",
            approved=True,
            publisher=self.publisher,
            author=self.journalist,
        )

        self.subscribed_journalist_article = Article.objects.create(
            title="Subscribed Journalist Article",
            content="Visible because journalist is subscribed",
            approved=True,
            publisher=self.other_publisher,
            author=self.journalist,
        )

        self.subscribed_publisher_article = Article.objects.create(
            title="Subscribed Publisher Article",
            content="Visible because publisher is subscribed",
            approved=True,
            publisher=self.publisher,
            author=self.other_journalist,
        )

        self.unsubscribed_article = Article.objects.create(
            title="Unsubscribed Article",
            content="Should not be visible",
            approved=True,
            publisher=self.other_publisher,
            author=self.other_journalist,
        )

        self.unapproved_article = Article.objects.create(
            title="Unapproved Article",
            content="Should not be visible",
            approved=False,
            publisher=self.publisher,
            author=self.journalist,
        )

        self.publisherless_article = Article.objects.create(
            title="Publisherless Article",
            content="Created without a publisher",
            approved=True,
            publisher=None,
            author=self.journalist,
        )

        # Subscriptions
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

    # =========================
    # TESTS
    # =========================

    def test_api_requires_authentication(self):
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, 403)

    def test_reader_receives_article_from_subscribed_publisher_and_journalist(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        titles = [article["title"] for article in response.data]

        self.assertIn("Subscribed Article", titles)

    def test_reader_receives_article_from_subscribed_journalist(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        titles = [article["title"] for article in response.data]

        self.assertIn("Subscribed Journalist Article", titles)

    def test_reader_receives_article_from_subscribed_publisher(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        titles = [article["title"] for article in response.data]

        self.assertIn("Subscribed Publisher Article", titles)

    def test_reader_does_not_receive_unsubscribed_content(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        titles = [article["title"] for article in response.data]

        self.assertNotIn("Unsubscribed Article", titles)

    def test_reader_does_not_receive_unapproved_articles(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        titles = [article["title"] for article in response.data]

        self.assertNotIn("Unapproved Article", titles)

    def test_reader_receives_publisherless_article_from_subscribed_journalist(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        titles = [article["title"] for article in response.data]

        self.assertIn("Publisherless Article", titles)