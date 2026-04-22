from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Publisher, Article

User = get_user_model()


class ArticleAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.reader = User.objects.create_user(
            username='reader1',
            password='testpass123',
            role='reader',
        )

        self.editor = User.objects.create_user(
            username='editor1',
            password='testpass123',
            role='editor',
        )

        self.journalist = User.objects.create_user(
            username='journalist1',
            password='testpass123',
            role='journalist',
        )

        self.other_journalist = User.objects.create_user(
            username='journalist2',
            password='testpass123',
            role='journalist',
        )

        self.publisher = Publisher.objects.create(
            name='Subscribed Publisher'
        )

        self.other_publisher = Publisher.objects.create(
            name='Unsubscribed Publisher'
        )

        self.subscribed_article = Article.objects.create(
            title='Subscribed Article',
            content='Visible to reader',
            approved=True,
            publisher=self.publisher,
            author=self.journalist,
        )

        self.unsubscribed_publisher_article = Article.objects.create(
            title='Other Publisher Article',
            content='Should not be visible',
            approved=True,
            publisher=self.other_publisher,
            author=self.journalist,
        )

        self.unsubscribed_journalist_article = Article.objects.create(
            title='Other Journalist Article',
            content='Should also not be visible',
            approved=True,
            publisher=self.publisher,
            author=self.other_journalist,
        )

        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

    def test_api_requires_authentication(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 403)

    def test_reader_receives_subscribed_content(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)

        titles = [article['title'] for article in response.data]
        self.assertIn('Subscribed Article', titles)

    def test_reader_does_not_receive_unsubscribed_publisher_content(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)

        titles = [article['title'] for article in response.data]
        self.assertNotIn('Other Publisher Article', titles)

    def test_reader_does_not_receive_unsubscribed_journalist_content(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)

        titles = [article['title'] for article in response.data]
        self.assertNotIn('Other Journalist Article', titles)