from django.urls import path
from playlist.views import *

app_name = 'playlist'

urlpatterns = [
    path('show_playlist', show_playlist, name='show_playlist'),
    path('user_playlist/<uuid:playlist_id>/', user_playlist, name='user_playlist'),
    path('delete_song/<uuid:song_id>/', delete_song, name='delete_song'),
    # path('add_song/',add_song, name='add_song'),
    path('view_song/<uuid:song_id>/', view_song, name='view_song')
]