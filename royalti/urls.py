from django.urls import path
from royalti.views import *

app_name = 'royalti'

urlpatterns = [
    path('', royalti, name='royalti'),
]