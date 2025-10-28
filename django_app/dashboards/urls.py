"""
URL configuration for dashboards app.
"""
from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('dashboards/', views.dashboard_list_page, name='dashboard_list_page'),
    path('dashboard/<str:dashboard_uuid>/', views.dashboard_view, name='dashboard_view'),

    # API endpoints
    path('api/dashboards/', views.dashboard_list_api, name='dashboard_list_api'),
    path('api/dashboard/<str:dashboard_uuid>/', views.dashboard_info_api, name='dashboard_info_api'),
    path('api/guest-token/', views.get_guest_token, name='get_guest_token'),
]
