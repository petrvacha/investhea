from django.urls import path, include
from . import views
from django.conf.urls import url
from web import views as core_views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('query-ticker-list/', views.query_ticker_list, name="query_ticker_list"),
    path('query-exchange-list/', views.query_exchange_list, name="query_exchange_list"),
    path('form-new-holding/', views.form_new_holding, name="form_new_holding"),
    path('add-new-holding/', views.add_new_holding, name="add_new_holding"),
    path('form-sell/<str:ticker>/', views.form_sell, name="form_sell"),
    path('security-transactions/<str:ticker>/', views.security_transactions, name="security_transactions"),
    path('delete-users-transaction/', views.delete_users_transaction_action, name="delete_users_transaction_action"),
    path('admin-dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('update-list-of-exchanges/', views.update_exchanges, name="update_exchanges"),
    path('download-list-of-stocks/', views.download_list_of_stocks, name="download_list_of_stocks"),
    path('', include('django.contrib.auth.urls')),
    url(r'^account_activation_sent/$', core_views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,35})/$', core_views.activate, name='activate'),
]
