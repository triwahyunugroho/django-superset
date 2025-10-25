from django.urls import path
from . import views
from .views_guest_token import generate_guest_token_direct

app_name = 'budget'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Alternative guest token endpoint (direct JWT generation)
    path('guest-token/<str:dashboard_id>/', generate_guest_token_direct, name='guest-token-direct'),
]
