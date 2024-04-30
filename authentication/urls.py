from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('register/user/', register_user, name='register_user'),
    path('register/label/', register_label, name='register_label'),
]