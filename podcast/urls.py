from django.urls import path
from podcast.views import play_podcast

app_name = 'podcast'

urlpatterns = [
    path('', play_podcast, name='play_podcast'),
]