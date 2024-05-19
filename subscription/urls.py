from django.urls import path
from subscription.views import *

app_name = 'subscription'

urlpatterns = [
    path('', subs_page, name='subscriptions'),
    path('checkout/<str:jenis_paket>/', checkout, name='checkout'),
    path('history/', history, name='history')
]