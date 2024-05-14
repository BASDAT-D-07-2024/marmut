from django.urls import path
from album.views import *

app_name = 'album'

urlpatterns = [
    path('', list_album, name='list_album'),
    path('create/', create_album, name='create_album'),
    path('<str:id>/', view_album, name='view_album'),
]