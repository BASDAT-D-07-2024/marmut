from django.urls import path
from podcast.views import *

app_name = 'podcast'

urlpatterns = [
    path('play-podcast/<uuid:id_konten>', play_podcast, name='play_podcast'),
    path('create-podcast/', create_podcast, name='create_podcast'),
    path('', list_podcast, name='list_podcast'),
    path('create-ep/<uuid:id_konten>', create_ep_podcast, name='create_ep_podcast'),
    path('list-ep/<uuid:id_konten>/', list_ep_podcast, name='list_ep_podcast'),
    path('delete/<uuid:id_konten>/', delete_podcast, name='delete_podcast'),
    path('delete/ep/<uuid:id_episode>/', delete_ep, name='delete_ep'),
]