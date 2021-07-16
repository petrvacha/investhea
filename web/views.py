from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from investhea.settings import EMAIL_HOST_USER
from web.models import Currency, User, Security, Exchange, UsersMoneyTransaction
from web.forms import SellForm, SignUpForm
from web.tokens import account_activation_token
from web.services.security import import_securities
from web.services.settings import save_settings
from web.services.exchange import import_exchanges
from web.services.users_securities import buy_security, get_users_securities, sell_security, is_sell_number_okay, get_users_transactions, delete_users_security_transaction
from django.template.defaulttags import register
from django.core.exceptions import ObjectDoesNotExist
from web.services.users_money_transaction import get_money_transactions, delete_money_transaction, add_money_transaction, get_free_cash
from datetime import datetime
import json


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def home(request):
    return render(request, 'home/home.html')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Investhea Account'
            message = render_to_string('register/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message, EMAIL_HOST_USER, fail_silently=False)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, "register/register.html", {
        'form': form
    })


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'register/account_activation_invalid.html')


def account_activation_sent(request):
    return render(request, "register/account_activation_sent.html")


@login_required
def query_ticker_list(request):
    query = request.GET.get('query', None)
    if query:
        start_tickers = list(Security.objects.filter(Q(ticker__istartswith=query)).values())
        tickers = list(Security.objects.filter(Q(ticker__contains=query) & ~Q(ticker__istartswith=query)).values())
        names = list(Security.objects.filter(Q(name__contains=query) & ~Q(ticker__istartswith=query) & ~Q(ticker__contains=query)).values())
        response = [*start_tickers, *tickers, *names]
    else:
        response = []

    return JsonResponse(response[0:10], safe=False)


@login_required
def query_exchange_list(request):
    exchanges = list(Exchange.objects.all().values())
    return JsonResponse(exchanges, safe=False)


@login_required
def dashboard(request):
    securities = get_users_securities(user=request.user)
    free_cash = get_free_cash(user=request.user)
    return render(request, "dashboard/dashboard.html", {
        "securities": securities,
        "free_cash": free_cash
    })


@login_required
def add_new_holding(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        buy_security(
            ticker=data["ticker"],
            user=request.user,
            price=data["price"],
            fee=data["fee"],
            quantity=data["quantity"],
            date=datetime.strptime(data["date"], '%d/%m/%Y'),
        )
    except Exception:
        return JsonResponse({"success": False, "message": "Problem with adding the new holding."}, status=500)

    return JsonResponse({"success": True, "message": "New holding has been successfully added."})


@login_required
def form_new_holding(request):
    return render(request, "holding/form_new_holding.html", {
        "var_url_autocomplete_query": reverse(query_ticker_list),
        "var_url_query_exchange_list": reverse(query_exchange_list),
        "var_url_add_new_holding": reverse(add_new_holding),
        "var_url_dashboard": reverse(dashboard),
    })


@login_required
def form_sell(request, ticker):
    if request.method == 'POST':
        form = SellForm(request.POST)

        if form.is_valid():
            if is_sell_number_okay(user=request.user, ticker=ticker, quantity=form.cleaned_data['quantity']):
                sell_security(
                    ticker=ticker,
                    user=request.user,
                    price=form.cleaned_data['price'],
                    fee=form.cleaned_data['fee'],
                    quantity=form.cleaned_data['quantity'],
                    date=form.cleaned_data['date'],
                )
                messages.success(request, 'Your holding has been successfully sold.')
                return redirect('dashboard')
            else:
                messages.error(request, 'You sell more than you have.')
        else:
            messages.error(request, 'An error occurred.')

    else:
        form = SellForm(initial={
            'ticker': ticker
        },)

    return render(request, "holding/form_sell.html", {
        "form": form,
        "ticker": ticker,
    })


@staff_member_required
def admin_dashboard(request):
    return render(request, "dashboard/admin-dashboard.html")


@staff_member_required
def download_list_of_stocks(request):
    try:
        import_securities()
    except Exception:
        response = {"success": False, "message": "Problem with the data processing."}
        return JsonResponse(response, status=500)

    return JsonResponse({"success": True, "message": "List of Stocks has been successfully updated."})


@login_required
def delete_money_transaction_action(request):
    data = json.loads(request.body.decode('utf-8'))
    transaction_id = data["transaction_id"]
    try:
        delete_money_transaction(user=request.user, transaction_id=transaction_id)
    except Exception:
        response = {"success": False, "message": "Problem with the data deleting."}
        return JsonResponse(response, status=500)

    return JsonResponse({"success": True, "message": "The transaction has been successfully deleted."})


@login_required
def money_transactions(request):
    if request.method == 'GET':
        transactions = get_money_transactions(user=request.user)
        return render(request, "money_transactions/money_transactions.html", {
            "var_transactions": list(transactions),
            "var_url_delete_users_transaction": reverse(delete_money_transaction_action)
        })
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            add_money_transaction(user=request.user,
                                  amount=data.amount,
                                  currency_id=data.currency_id,
                                  date=data.date)
        except Exception:
            response = {"success": False, "message": "Problem with the data deleting."}
            return JsonResponse(response, status=500)

        return JsonResponse({"success": True, "message": "The transaction has been successfully deleted."})


@login_required
def form_new_money_transactions(request):
    transaction_types = UsersMoneyTransaction.TRANSACTION_TYPES
    currencies = Currency.objects.all().values_list('id', 'name')
    return render(request, "money_transactions/form_new_money_transaction.html", {
        "var_url_users_money_transactions": reverse(money_transactions),
        "var_url_add_new_money_transaction": reverse(add_new_money_transaction),
        "transaction_types": transaction_types,
        "currencies": currencies
    })


@login_required
def add_new_money_transaction(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        add_money_transaction(
            amount=data["amount"],
            user=request.user,
            currency_id=data["currency_id"],
            transacted_at=datetime.strptime(data["transacted_at"], '%d/%m/%Y'),
            transaction_type_id=data["transaction_type_id"],
            note=data["note"],
        )
    except Exception:
        return JsonResponse({"success": False, "message": "Problem with adding the new money transaction."}, status=500)

    return JsonResponse({"success": True, "message": "New money transaction has been successfully added."})


@login_required
def security_transactions(request, ticker):
    transactions = get_users_transactions(user=request.user, ticker=ticker)
    ticker_string, _ = ticker.split('.')
    return render(request, "security_transactions/security_transactions.html", {
        "security": ticker_string,
        "var_transactions": list(transactions),
        "var_url_delete_users_transaction": reverse(delete_users_security_transaction)
    })


@login_required
def delete_users_security_transaction_action(request):
    data = json.loads(request.body.decode('utf-8'))
    transaction_id = data["transaction_id"]

    try:
        delete_users_security_transaction(user=request.user, transaction_id=transaction_id)
    except ObjectDoesNotExist:
        return JsonResponse({"success": False, "message": "The transaction does not exist."}, status=500)

    return JsonResponse({"success": True, "message": "The transaction has been successfully deleted."})


@staff_member_required
def update_exchanges(request):
    try:
        import_exchanges()
    except Exception:
        return JsonResponse({"success": False, "message": "Problem with the data processing."}, status=500)

    return JsonResponse({"success": True, "message": "List of exchanges has been successfully updated."})


@login_required
def users_settings(request):
    if request.method == 'GET':
        currencies = Currency.objects.all().values_list('id', 'name')
        return render(request, "users_settings/users_settings.html", {
            "currencies": currencies,
        })
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        save_settings(user=request.user,
                      first_name=data['first_name'],
                      last_name=data['last_name'],
                      currency_id=data['currency_id'],
                      email=data['email'],)
        return JsonResponse({"success": True, "message": "Settings has been successfully updated."})
