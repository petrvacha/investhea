from web.models import Currency, User, UsersMoneyTransaction
from datetime import datetime
from django.db.models import F, Func, Value, CharField, Sum


def add_money_transaction(*,
                          amount: int,
                          user: User,
                          currency_id: int,
                          transaction_type_id: int,
                          note: str,
                          transacted_at: datetime.date,) -> UsersMoneyTransaction:

    currency = Currency.objects.get(pk=currency_id)

    users_money_transaction = UsersMoneyTransaction()
    users_money_transaction.user = user
    users_money_transaction.amount = amount
    users_money_transaction.currency = currency
    users_money_transaction.transacted_at = transacted_at
    users_money_transaction.direction = UsersMoneyTransaction.DIRECTION_INCOME
    users_money_transaction.transaction_type_id = transaction_type_id
    users_money_transaction.note = note
    users_money_transaction.full_clean()
    users_money_transaction.save()

    return users_money_transaction


def get_money_transactions(*, user: User,) -> dict:
    return UsersMoneyTransaction.objects.filter(user=user).annotate(formatted_date=Func(F('transacted_at'),
                                                                                        Value('%d/%m/%Y'),
                                                                                        function='DATE_FORMAT',
                                                                                        output_field=CharField())).values()


def delete_money_transaction(*,
                             user: User,
                             transaction_id: int) -> None:
    UsersMoneyTransaction.objects.get(id=transaction_id, user=user).delete()


def get_free_cash(*, user: User) -> int:
    free_cash = UsersMoneyTransaction.objects.filter(user=user).values('currency_id').annotate(sum=Sum('amount'))
    return free_cash
