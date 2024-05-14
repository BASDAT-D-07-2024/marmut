from django.urls import path
from song.views import *

app_name = 'song'

urlpatterns = [
    path('', show_song, name='show_song'),
]