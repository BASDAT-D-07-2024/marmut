from django.urls import path
from search.views import *

app_name = 'search'

urlpatterns = [
    path('', search_result, name='search_result'),
]