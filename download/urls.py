from django.urls import path
from download.views import *

app_name = 'download'

urlpatterns = [
    path('', list_download, name='list_album'),
]