from django.urls import path
from subscription.views import *

app_name = 'subscription'

urlpatterns = [
    path('', subs_page, name='subs_page'),
]