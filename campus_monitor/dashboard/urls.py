from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_page, name='search'),
    path('entities/', views.entity_list, name='entity_list'),
    path('entity/<int:pk>/', views.entity_detail, name='entity_detail'),
    path('identifiers/', views.identifiers_list, name='identifiers_list'),
    path('swipes/', views.swipes_list, name='swipes_list'),
    path('wifi/', views.wifi_list, name='wifi_list'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('library/', views.library_list, name='library_list'),
    path('notes/', views.notes_list, name='notes_list'),
    path('resolution-links/', views.resolution_links_list, name='resolution_links_list'),
    path('provenance/', views.provenance_list, name='provenance_list'),
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
