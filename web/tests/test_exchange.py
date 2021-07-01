from django.test import TestCase
from web.services.exchange import process_import_exchanges
from web.models import Country, Exchange


class ExchangeTest(TestCase):
    def test_process_import_exchanges(self):
        data_mockup = [{
            'name': 'NASDAQ',
            'code': 'XNGS',
            'country': 'United States',
            'timezone': 'America/New_York'}]

        process_import_exchanges(data_mockup)
        q1 = Exchange.objects.get(name="NASDAQ")
        self.assertEqual(q1.time_zone, data_mockup[0]["timezone"])
        q2 = Country.objects.get(name="United States")
        self.assertIsNotNone(q2)
