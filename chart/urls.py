from django.urls import path
from chart.views import chart_list, chart_detail

app_name = 'chart'

urlpatterns = [
    path('list/', chart_list, name='chart_list'),
    path('detail/', chart_detail, name='chart_detail'),
]