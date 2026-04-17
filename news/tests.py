from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Publisher, Article

User = get_user_model()


class ArticleAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create users
        self.reader = User.objects.create_user(
            username="reader",
            password="testpass123",
            role="reader"
        )

        self.journalist = User.objects.create_user(
            username="journalist",
            password="testpass123",
            role="journalist"
        )

        # Create publisher
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )

        # Create article
        self.article = Article.objects.create(
            title="Test Article",
            content="Test Content",
            approved=True,
            publisher=self.publisher,
            author=self.journalist
        )

        # Subscribe reader to publisher
        self.reader.subscribed_publishers.add(self.publisher)

    # -------------------------
    # TEST 1: API AUTH REQUIRED 
    # -------------------------
    def test_api_requires_auth(self):
        response = self.client.get('/api/articles/')
        self.assertIn(response.status_code, [401, 403])

    # -------------------------
    # TEST 2: READER GETS DATA
    # -------------------------
    def test_reader_can_access_articles(self):
        self.client.login(username="reader", password="testpass123")
        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # -------------------------
    # TEST 3: JOURNALIST GETS DATA
    # -------------------------
    def test_journalist_can_access_articles(self):
        self.client.login(username="journalist", password="testpass123")
        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)