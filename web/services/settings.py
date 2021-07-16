from web.models import Currency, User, UsersMoneyTransaction


def save_settings(*,
                  user: User,
                  currency_id: str,
                  email: str,
                  first_name: str,
                  last_name: str,) -> UsersMoneyTransaction:

    currency = Currency.objects.get(pk=currency_id)

    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.profile.currency = currency
    user.full_clean()
    user.save()
