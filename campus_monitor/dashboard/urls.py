from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_page, name='search'),
    path('timeline/', views.timeline_page, name='timeline'),
    path('predict/', views.predict_page, name='predict'),
    path('alerts/', views.alerts_page, name='alerts'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/timeline/', views.api_timeline, name='api_timeline'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/alerts/', views.api_alerts, name='api_alerts'),
]
