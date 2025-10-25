"""
URL configuration for superset-django integration project.
"""
from django.contrib import admin
from django.urls import path, include
from budget.views_superset import fetch_superset_guest_token

urlpatterns = [
    path('admin/', admin.site.urls),
    # Override django-superset-integration guest_token endpoint to fix https bug
    path('superset_integration/guest_token/<slug:dashboard_id>', fetch_superset_guest_token, name='guest-token'),
    path('superset_integration/', include('django_superset_integration.urls')),
    path('api/', include('budget.urls')),
    path('', include('budget.urls')),
]
