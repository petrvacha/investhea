from web.models import Exchange, UsersSecurities, User, Security
from datetime import datetime


def create_users_security(*,
                          ticker: str,
                          user: User,
                          price: float,
                          fee: float,
                          quantity: int,
                          date: str,
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
    users_securities.date = datetime.strptime(date, '%d/ %m/ %Y')
    users_securities.direction = UsersSecurities.BUY
    users_securities.full_clean()
    users_securities.save()

    return users_securities


def buy_security(*,
                 ticker: str,
                 user: User,
                 price: float,
                 fee: float,
                 quantity: int,
                 date: str,) -> UsersSecurities:
    return create_users_security(ticker=ticker,
                                 user=user,
                                 price=price,
                                 fee=fee,
                                 quantity=quantity,
                                 date=date,
                                 direction=UsersSecurities.BUY)


def get_users_securities(*,
                         user: User,) -> dict:
    users_securities = UsersSecurities.objects.filter(user=user).order_by('date')

    results = {'transactions': {}, 'currents': {}}

    for transaction in users_securities:
        ticker_name = transaction.security.ticker
        if ticker_name not in results['transactions'].keys():
            results['transactions'][ticker_name] = []
            results['currents'][ticker_name] = []

        transaction_data = {'ticker': ticker_name,
                            'company_name': transaction.security.name,
                            'quantity': transaction.quantity,
                            'purchased_price': transaction.price,
                            'purchased_value': transaction.price * transaction.quantity,
                            'date': transaction.date}

        results['transactions'][ticker_name].append(transaction_data)

        if transaction.direction == UsersSecurities.BUY:
            results['currents'][ticker_name].insert(0, transaction_data)
        else:
            remove_items = []
            count_diff = transaction.quantity

            for i, previous_transaction in enumerate(results['currents'][ticker_name]):
                count_diff = count_diff - previous_transaction.quantity
                if count_diff == 0:
                    remove_items.insert(0, i)
                    break
                elif count_diff > 0:
                    remove_items.insert(0, i)
                    continue
                else:
                    results['currents'][ticker_name][i]['quantity'] = -1 * count_diff
                    break

            for i in remove_items:
                del results['currents'][ticker_name][i]

    return results
