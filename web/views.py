from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from web.models import User
from web.models import Security
from web.models import Exchange
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from web.forms import SignUpForm
from web.tokens import account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from investhea.settings import EMAIL_HOST_USER
from investhea.settings import ALPHA_VANTAGE_API_KEY
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from web.modules.alpha_vantage import AlphaVantageRequestor as avr
from django.urls import reverse
from django.db.models import Q


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
    return render(request, "dashboard/dashboard.html", {
        "var_url_autocomplete_query": reverse(query_ticker_list),
        "var_url_query_exchange_list": reverse(query_exchange_list),
    })


@staff_member_required
def admin_dashboard(request):
    return render(request, "dashboard/admin-dashboard.html")


@staff_member_required
def download_list_of_stocks(request):

    response = {
        "success": True,
        "message": "List of Stocks has been successfully updated.",
    }

    avrequestor = avr(ALPHA_VANTAGE_API_KEY)
    data = avrequestor.getListOfStocks()
    try:
        Security.process_import(data)
    except AssertionError:
        response["success"] = False
        response["message"] = "Problem with the data processing."

    return JsonResponse(response)
