from django.urls import path
from album.views import *

app_name = 'album'

urlpatterns = [
    path('', list_album, name='list_album'),
    path('create/', create_album, name='create_album'),
    path('delete/<uuid:album_id>/', delete_album, name='delete_album'),
    path('create/song/<uuid:album_id>/', create_song, name='create_song'),
    path('delete/song/<uuid:song_id>/', delete_song, name='delete_song'),
    path('<str:id>/', view_album, name='view_album'),
]