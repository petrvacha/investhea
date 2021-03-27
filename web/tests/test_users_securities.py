from django.test import TestCase
from django.contrib.auth import get_user_model
from web.models import Exchange, UsersSecurities, Security
from web.services.users_securities import buy_security


class UsersSecuritiesTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(password='Test124', email='test@example.com')
        self.user.save()

        exchange = Exchange.objects.create(name="NYSE", country=Exchange.USA)
        Security.objects.create(ticker="IBM", exchange=exchange, security_type=Security.STOCK)

    def tearDown(self):
        self.user.delete()

    def test_buy_security(self):
        buy_security(
            ticker='IBM.NYSE',
            user=self.user,
            price=10.0,
            fee=5.0,
            quantity=1000,
            date='25/ 12/ 2020')

        holds = UsersSecurities.objects.filter(user=self.user)
        self.assertTrue(len(holds) > 0)
        self.assertTrue(holds[0].price == 10.0)
