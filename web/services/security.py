from twelvedata import TDClient
from investhea.settings import TWELVE_DATA_API_KEY
from datetime import datetime
from django.utils import timezone
from web.models import Exchange, Security, SecurityType
from django.db import transaction

ALPHA_VANTAGE_SOURCE = 'Aplha Vantage'
TWELVE_DATA_SOURCE = 'Twelve Data'


def import_securities():
    td = TDClient(apikey=TWELVE_DATA_API_KEY)
    securities_data = td.get_stocks_list().as_json()
    process_import_securities(securities_data)


def process_import_securities(securities_data):
    sync_timestampt = datetime.now(tz=timezone.utc)
    db_exchanges = dict(Exchange.objects.values_list('name', 'id'))
    for security in securities_data:
        with transaction.atomic():
            security_type, _ = SecurityType.objects.update_or_create(
                name=security['type'],
                defaults={'show': False})
        with transaction.atomic():
            Security.objects.update_or_create(
                ticker=security['symbol'],
                exchange_id=db_exchanges[security['exchange']],
                defaults={
                    'name': security['name'],
                    'data_source': TWELVE_DATA_SOURCE,
                    'status': True,
                    'security_type': security_type,
                    'sync_at': sync_timestampt})
