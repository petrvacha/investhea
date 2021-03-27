from django.test import TestCase
from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse
from django.conf import settings


class SigninTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(password='Test124', email='test@example.com')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(email='test@example.com', password='Test124')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(email='wrong@example.com', password='Test124')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_password(self):
        user = authenticate(email='test@example.com', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_only_for_logged_in(self):
        restricted_pages = {
            'dashboard': 'dashboard'
        }

        for page_name, page_url in restricted_pages.items():
            response = self.client.get(reverse(page_name))
            self.assertRedirects(response, settings.LOGIN_URL + '?next=/' + page_url + '/')
