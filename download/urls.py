from django.urls import path
from download.views import *

app_name = 'download'

urlpatterns = [
    path('', list_download, name='list_download'),
    path('delete/<uuid:id_song>', delete_download, name='delete_download'),

    path('/', list_download, name='list_download'),
    path('/delete/<uuid:id_song>/', delete_download, name='delete_download'),
]