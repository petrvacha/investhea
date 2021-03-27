from django.test import TestCase
from web.services.security import process_import
from web.models import Exchange, Security
import pandas as pd
import datetime


class SecurityTest(TestCase):

    def test_security_process_import(self):
        data_mockup = [
            ["symbol", "name", "exchange", "assetType", "ipoDate", "delistingDate", "status"],
            ["AAAAATEST", "AAAAATESTNAME", "NYSE", "ETF", "1999-11-18", "null", "Active"],
            ["AAAAATEST2", "AAAAATESTNAME2", "TEST", "Stock", "1999-11-18", "null", "Active"]
        ]

        data_mockup_frame = pd.DataFrame(data=data_mockup)
        process_import(data_mockup_frame)

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
        process_import(renamed_data_mockup_frame)
        q3 = Security.objects.get(ticker="AAAAATEST")
        self.assertEqual(q3.name, renamed_data_mockup[1][1])
