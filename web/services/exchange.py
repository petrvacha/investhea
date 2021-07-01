from twelvedata import TDClient
from investhea.settings import TWELVE_DATA_API_KEY
from web.models import Country, Exchange
from datetime import datetime
from django.utils import timezone


def import_exchanges():
    td = TDClient(apikey=TWELVE_DATA_API_KEY)
    exchanges_data = td.get_exchanges_list().as_json()
    process_import_exchanges(exchanges_data)


def process_import_exchanges(exchanges_data):
    sync_timestampt = datetime.now(tz=timezone.utc)
    db_exchanges = dict(Exchange.objects.values_list('name', 'id'))
    db_countries = dict(Country.objects.values_list('name', 'id'))

    for exchange in exchanges_data:
        if exchange['name'] in db_exchanges:
            db_exchange = Exchange.objects.get(pk=db_exchanges[exchange['name']])
            db_exchange.sync_at = sync_timestampt
            db_exchange.save()
        else:
            new_exchange = Exchange()
            new_exchange.name = exchange['name']
            new_exchange.time_zone = exchange['timezone']
            new_exchange.sync_at = sync_timestampt

            if exchange['country'] in db_countries:
                new_exchange.country_id = db_countries[exchange['country']]
            else:
                country = Country.objects.create(name=exchange['country'])
                new_exchange.country = country
                db_countries = dict(Country.objects.values_list('name', 'id'))
            new_exchange.save()
            db_exchanges = dict(Exchange.objects.values_list('name', 'id'))
