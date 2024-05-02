from django.urls import path
from podcast.views import *

app_name = 'podcast'

urlpatterns = [
    path('play-podcast/', play_podcast, name='play_podcast'),
    path('create-podcast', create_podcast, name='create_podcast'),
    path('podcast-list', list_podcast, name='list_podcast'),
    path('create-ep', create_ep_podcast, name='create_ep_podcast'),
    path('list-ep', list_ep_podcast, name='list_ep_podcast'),
]