from web.models import Exchange, UsersSecurities, User, Security
from datetime import datetime
from django.db.models import Sum
from django.db.models import ExpressionWrapper, FloatField, F


def create_users_security(*,
                          ticker: str,
                          user: User,
                          price: float,
                          fee: float,
                          quantity: int,
                          date: datetime.date,
                          direction: int,) -> UsersSecurities:
    ticker_string, exchange_string = ticker.split('.')

    exchange = Exchange.objects.get(name=exchange_string)
    security = Security.objects.get(ticker=ticker_string, exchange=exchange)

    users_securities = UsersSecurities()
    users_securities.user = user
    users_securities.security = security
    users_securities.price = price
    users_securities.fee = fee
    users_securities.quantity = quantity
    users_securities.date = date
    users_securities.direction = direction
    users_securities.full_clean()
    users_securities.save()

    return users_securities


def buy_security(*,
                 ticker: str,
                 user: User,
                 price: float,
                 fee: float,
                 quantity: int,
                 date: datetime.date,) -> UsersSecurities:
    return create_users_security(ticker=ticker,
                                 user=user,
                                 price=price,
                                 fee=fee,
                                 quantity=quantity,
                                 date=date,
                                 direction=UsersSecurities.BUY)


def is_sell_number_okay(*,
                        user: User,
                        ticker: str,
                        quantity: int,) -> bool:
    ticker_string, exchange_string = ticker.split('.')
    exchange = Exchange.objects.get(name=exchange_string)
    security = Security.objects.get(ticker=ticker_string, exchange=exchange)
    result = UsersSecurities.objects.filter(user=user, security=security).aggregate(Sum('quantity'))

    if result['quantity__sum'] is None:
        return False
    else:
        return result['quantity__sum'] >= quantity


def sell_security(*,
                  ticker: str,
                  user: User,
                  price: float,
                  fee: float,
                  quantity: int,
                  date: datetime.date,) -> UsersSecurities:
    return create_users_security(ticker=ticker,
                                 user=user,
                                 price=price,
                                 fee=fee,
                                 quantity=quantity,
                                 date=date,
                                 direction=UsersSecurities.SELL)


def get_users_securities(*,
                         user: User,) -> dict:
    users_securities = UsersSecurities.objects.filter(user=user).order_by('date')

    results = {'transactions': {}, 'hold': {}, 'sold': {}, 'ticker_info': {}}

    for transaction in users_securities:
        ticker = transaction.security.ticker + '.' + transaction.security.exchange.name
        if ticker not in results['transactions'].keys():
            results['transactions'][ticker] = []
            results['ticker_info'][ticker] = {
                'ticker_name': ticker,
                'company_name': transaction.security.name,
            }

        transaction_data = {'quantity': transaction.quantity,
                            'purchased_value': transaction.price * transaction.quantity,
                            'fee': transaction.fee,
                            'date': transaction.date,
                            'direction': transaction.direction,
                            }

        results['transactions'][ticker].append(transaction_data)

    for ticker in results['transactions']:
        total_quantity = 0
        total_cost = 0
        total_fee = 0
        last_fee = 0
        for transaction_data in results['transactions'][ticker]:
            if transaction_data['direction'] == UsersSecurities.BUY:
                total_quantity += transaction_data['quantity']
                total_cost -= transaction_data['purchased_value']
            else:
                total_quantity -= transaction_data['quantity']
                total_cost += transaction_data['purchased_value']
            last_fee = transaction_data['fee']
            total_fee += last_fee

        if total_quantity > 0:
            results['hold'][ticker] = {
                'total_quantity': total_quantity,
                'total_cost': total_cost,
                'total_fee': total_cost,
                'last_fee': last_fee,
            }
        else:
            results['sold'][ticker] = {
                'quantity': total_quantity,
                'total_cost': total_cost,
                'total_fee': total_cost,
                'last_fee': last_fee,
            }

    return results


def get_users_transactions(*,
                           user: User,
                           ticker: str) -> dict:
    ticker_string, exchange_string = ticker.split('.')
    exchange = Exchange.objects.get(name=exchange_string)
    security = Security.objects.get(ticker=ticker_string, exchange=exchange)
    transactions = UsersSecurities.objects.filter(user=user, security=security).annotate(value=ExpressionWrapper(F('quantity') * F('price'), output_field=FloatField())).values()
    return transactions


def delete_users_transaction(*,
                             user: User,
                             transaction_id: int) -> None:
    UsersSecurities.objects.get(id=transaction_id, user=user).delete()
