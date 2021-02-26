from django.test import TestCase
from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse
from django.conf import settings
from web.models import Security
from web.models import Exchange
import pandas as pd
import datetime


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

    def test_security_process_import(self):
        data_mockup = [
            ["symbol", "name", "exchange", "assetType", "ipoDate", "delistingDate", "status"],
            ["AAAAATEST", "AAAAATESTNAME", "NYSE", "ETF", "1999-11-18", "null", "Active"],
            ["AAAAATEST2", "AAAAATESTNAME2", "TEST", "Stock", "1999-11-18", "null", "Active"]
        ]

        data_mockup_frame = pd.DataFrame(data=data_mockup)
        Security.process_import(data_mockup_frame)

        q1 = Security.objects.get(ticker="AAAAATEST")
        security_types = dict(Security.TYPES)
        self.assertEqual(q1.name, data_mockup[1][1])
        self.assertEqual(q1.exchange.name, data_mockup[1][2])
        self.assertEqual(security_types[q1.security_type], data_mockup[1][3])
        self.assertEqual(q1.ipo_date, datetime.datetime.strptime(data_mockup[1][4], "%Y-%m-%d").date())
        self.assertEqual(q1.delisting_date, None)
        self.assertEqual(q1.status, (data_mockup[1][6] == "Active"))

        q2 = Exchange.objects.get(name="TEST")
        self.assertEqual(q2.country, 1)

        renamed_data_mockup = [
            ["symbol", "name", "exchange", "assetType", "ipoDate", "delistingDate", "status"],
            ["AAAAATEST", "RENAME", "NYSE", "ETF", "1999-11-18", "null", "Active"]
        ]

        renamed_data_mockup_frame = pd.DataFrame(data=renamed_data_mockup)
        Security.process_import(renamed_data_mockup_frame)
        q3 = Security.objects.get(ticker="AAAAATEST")
        self.assertEqual(q3.name, renamed_data_mockup[1][1])
