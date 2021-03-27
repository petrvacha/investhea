from web.models import Exchange, Security
import pandas as pd


def process_import(data):
    exchanges = Exchange.objects.all()
    list_exchanges = {}
    for exchange in exchanges:
        list_exchanges[exchange.name] = exchange

    for row in data[1:].itertuples(index=False, name='Pandas'):
        existingSecurity = Security.objects.filter(ticker=row[0])
        if existingSecurity.exists():
            security = existingSecurity.first()
        else:
            security = Security()
        security.ticker = row[0]
        security.name = row[1]
        if row[2] in list_exchanges:
            security.exchange = list_exchanges[row[2]]
        else:
            newExchange = Exchange.objects.create(name=row[2])
            list_exchanges[row[2]] = newExchange
            security.exchange = list_exchanges[row[2]]

        security.security_type = Security.STOCK if row[3] == "Stock" else Security.ETF
        security.ipo_date = row[4]
        if pd.notnull(row[5]) and row[5] != "null":
            security.delisting_date = row[5]
        security.status = True if row[6] == "Active" else False
        security.save()
