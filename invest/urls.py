from django.urls import path
from . import views

app_name = 'invest'

urlpatterns = [
    path('', views.index, name='index'),
    path('chart', views.chart, name='chart'),
    path('chart/result/', views.chart_result, name='chart_result'),
    path('info', views.info, name='info'),
    path('info/result/', views.info_result, name='info_result'),
    path('memo', views.memo, name='memo'),
    path('memo/<int:memo_id>/', views.memo_content, name='memo_content'),
    path('memo/create/', views.memo_create, name='memo_create'),
]