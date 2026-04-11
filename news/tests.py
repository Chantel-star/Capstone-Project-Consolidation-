from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import (
    Article,
    Publisher,
    PublisherSubscription,
    JournalistSubscription
)

User = get_user_model()


class SubscribedArticlesAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # =========================
        # USERS
        # =========================
        self.reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='reader'
        )

        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='journalist'
        )

        self.other_journalist = User.objects.create_user(
            username='other_journalist',
            password='testpass123',
            role='journalist'
        )

        # =========================
        # PUBLISHERS
        # =========================
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='Test Description'
        )

        self.other_publisher = Publisher.objects.create(
            name='Other Publisher',
            description='Other Description'
        )

        # =========================
        # ARTICLES
        # =========================
        self.article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            approved=True,
            publisher=self.publisher,
            author=self.journalist
        )

        self.article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            approved=True,
            publisher=self.publisher,
            author=self.journalist
        )

        self.unapproved_article = Article.objects.create(
            title='Draft Article',
            content='Draft',
            approved=False,
            publisher=self.publisher,
            author=self.journalist
        )

        self.other_article = Article.objects.create(
            title='Other Article',
            content='Other Content',
            approved=True,
            publisher=self.other_publisher,
            author=self.other_journalist
        )

        # =========================
        # SUBSCRIPTIONS
        # =========================
        PublisherSubscription.objects.create(
            user=self.reader,
            publisher=self.publisher
        )

        JournalistSubscription.objects.create(
            user=self.reader,
            journalist=self.journalist
        )

    # =========================
    # TEST 1
    # =========================
    def test_authenticated_user_gets_correct_articles(self):
        self.client.login(username='reader', password='testpass123')

        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)

        titles = [article['title'] for article in response.data]

        self.assertIn('Article 1', titles)
        self.assertIn('Article 2', titles)
        self.assertNotIn('Draft Article', titles)
        self.assertNotIn('Other Article', titles)

    # =========================
    # TEST 2
    # =========================
    def test_unauthenticated_user_denied(self):
        response = self.client.get('/api/articles/')

        self.assertIn(response.status_code, [401, 403])

    # =========================
    # TEST 3
    # =========================
    def test_only_subscribed_content_returned(self):
        self.client.login(username='reader', password='testpass123')

        response = self.client.get('/api/articles/')

        titles = [article['title'] for article in response.data]

        self.assertNotIn('Other Article', titles)
        self.assertNotIn('Draft Article', titles)