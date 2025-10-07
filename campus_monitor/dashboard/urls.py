from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
    # Authentication
    path('accounts/login/', views.login_view, name='login'),
    # Render a friendly logged-out confirmation page after logout
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='dashboard/logged_out.html'), name='logout'),
    path('accounts/signup/', views.signup_view, name='signup'),
]
