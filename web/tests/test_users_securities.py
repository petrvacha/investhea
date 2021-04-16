from django.test import TestCase
from django.contrib.auth import get_user_model
from web.models import Exchange, UsersSecurities, Security
from web.services.users_securities import buy_security, sell_security, is_sell_number_okay, delete_users_transaction


class UsersSecuritiesTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(password='Test124', email='test@example.com')
        self.user.save()

        exchange = Exchange.objects.create(name="NYSE", country=Exchange.USA)
        Security.objects.create(ticker="IBM", exchange=exchange, security_type=Security.STOCK)
        exchange = Exchange.objects.create(name="NASDAQ", country=Exchange.USA)
        Security.objects.create(ticker="MSFT", exchange=exchange, security_type=Security.STOCK)

    def tearDown(self):
        self.user.delete()

    def test_buy_security(self):
        buy_security(
            ticker='IBM.NYSE',
            user=self.user,
            price=10.0,
            fee=5.0,
            quantity=1000,
            date='2020-12-25')

        holds = UsersSecurities.objects.filter(user=self.user)
        self.assertTrue(len(holds) > 0)
        self.assertTrue(holds[0].price == 10.0)

    def test_sell_security(self):
        sell_security(
            ticker='IBM.NYSE',
            user=self.user,
            price=10.0,
            fee=5.0,
            quantity=999,
            date='2020-12-26')

        sell = UsersSecurities.objects.filter(user=self.user, direction=UsersSecurities.SELL)
        self.assertTrue(len(sell) == 1)

    def test_is_sell_number_okay(self):
        buy_security(
            ticker='IBM.NYSE',
            user=self.user,
            price=10.0,
            fee=5.0,
            quantity=1000,
            date='2020-12-25')

        result = is_sell_number_okay(
            ticker='IBM.NYSE',
            user=self.user,
            quantity=1000,)

        self.assertTrue(result)

        result = is_sell_number_okay(
            ticker='IBM.NYSE',
            user=self.user,
            quantity=10000,)

        self.assertFalse(result)

        result = is_sell_number_okay(
            ticker='MSFT.NASDAQ',
            user=self.user,
            quantity=10000,)

        self.assertFalse(result)

    def test_delete_users_transaction(self):
        transaction = buy_security(
            ticker='IBM.NYSE',
            user=self.user,
            price=10.0,
            fee=5.0,
            quantity=1000,
            date='2020-12-25')

        transaction = UsersSecurities.objects.filter(user=self.user, id=transaction.pk)
        self.assertTrue(len(transaction) == 1)
        delete_users_transaction(
            transaction_id=transaction[0].pk,
            user=self.user,)

        transaction = UsersSecurities.objects.filter(user=self.user, id=transaction[0].pk)
        self.assertTrue(len(transaction) == 0)
