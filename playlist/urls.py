from django.urls import path
from playlist.views import *

app_name = 'playlist'

urlpatterns = [
    path('', show_playlist, name='show_playlist'),
    path('user-playlist/', user_playlist, name='user_playlist'),
]