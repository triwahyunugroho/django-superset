"""
Custom view untuk fix django-superset-integration bug
Bug: Package hardcode https:// di URL, padahal kita pakai http://
"""
import requests
from cryptography.fernet import Fernet

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_safe
from django.conf import settings

from django_superset_integration.models import SupersetDashboard


def create_rls_clause(user):
    """
    SQL clause to apply to the dashboard data
    """
    if not user:
        return [{"clause": "1=0"}]
    return [{"clause": "1=1"}]


@require_safe
def fetch_superset_guest_token(request, dashboard_id: str):
    """
    Get a guest token for integration of a Superset dashboard
    Fixed version that supports both http and https
    """
    try:
        with requests.Session() as session:
            dashboard = SupersetDashboard.objects.get(id=int(dashboard_id))
            dashboard_integration_id = dashboard.integration_id
            superset_domain = dashboard.domain.address
            superset_username = dashboard.domain.username

            # Use http:// instead of hardcoded https://
            protocol = "http"
            url = f"{protocol}://{superset_domain}/api/v1/security/login"

            def get_password(password):
                cipher_suite = Fernet(settings.ENCRYPTION_KEY)
                decrypted_password = cipher_suite.decrypt(password.encode())
                return decrypted_password.decode()

            params = {
                "provider": "db",
                "refresh": "True",
                "username": superset_username,
                "password": get_password(dashboard.domain.password),
            }

            session.headers.update({"Content-Type": "application/json"})
            response = session.post(url, json=params)

            if response.status_code != 200:
                return JsonResponse({
                    "error": "Failed to login to Superset",
                    "status_code": response.status_code,
                    "response": response.text
                }, status=500)

            access_token = response.json()["access_token"]

            session.headers.update({"Authorization": f"Bearer {access_token}"})
            url = f"{protocol}://{superset_domain}/api/v1/security/csrf_token/"
            response = session.get(url)

            if response.status_code != 200:
                return JsonResponse({
                    "error": "Failed to get CSRF token",
                    "status_code": response.status_code
                }, status=500)

            csrf_token = response.json()["result"]

            user = request.user
            rls = create_rls_clause(user)

            session.headers.update(
                {"X-CSRFToken": csrf_token, "Referer": f"{protocol}://{superset_domain}"}
            )

            params = {
                "resources": [
                    {
                        "id": dashboard_integration_id,
                        "type": "dashboard",
                    }
                ],
                "rls": rls,
                "user": {
                    "username": "guest",
                    "first_name": "Guest",
                    "last_name": "User",
                },
            }

            url = f"{protocol}://{superset_domain}/api/v1/security/guest_token/"
            response = session.post(url, json=params)

            if response.status_code != 200:
                return JsonResponse({
                    "error": "Failed to get guest token",
                    "status_code": response.status_code,
                    "response": response.text
                }, status=500)

            guest_token = response.json()["token"]

            return HttpResponse(guest_token)

    except SupersetDashboard.DoesNotExist:
        return JsonResponse({"error": f"Dashboard with id {dashboard_id} not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
