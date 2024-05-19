from django.urls import path
from playlist.views import *

app_name = 'playlist'

urlpatterns = [
    path('show_playlist', show_playlist, name='show_playlist'),
    path('create_playlist', create_playlist, name='create_playlist'),
    path('delete_playlist/<uuid:playlist_id>/', delete_playlist, name='delete_playlist'),
    path('edit_playlist/<uuid:playlist_id>/', edit_playlist, name='edit_playlust'),
    path('user_playlist/<uuid:playlist_id>/', user_playlist, name='user_playlist'),
    path('delete_song/<uuid:playlist_id>/<uuid:song_id>/', delete_song, name='delete_song'),
    path('add_song/<uuid:playlist_id>/', add_song, name='add_song'),
    path('play_song/<uuid:song_id>/', play_song, name='play_song'),
    path('add_to_playlist_from_song/<uuid:song_id>/', add_to_playlist_from_song, name='add_to_playlist_from_song'),
    path('play_playlist/<uuid:id_user_playlist>/', play_playlist, name='play_playlist'),
    # path('add_song_to_playlist/<uuid:playlist_id>/<uuid:song_id>/', add_song_to_playlist, name='add_song_to_playlist'),
    path('view_song/<uuid:playlist_id>/<uuid:song_id>/', view_song, name='view_song')

]