from django.urls import path, include
from . import views
from django.conf.urls import url
from web import views as core_views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('admin-dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('download-list-of-stocks/', views.download_list_of_stocks, name="download_list_of_stocks"),
    path('', include('django.contrib.auth.urls')),
    url(r'^account_activation_sent/$', core_views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,35})/$', core_views.activate, name='activate'),
]
