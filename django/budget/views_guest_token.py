"""
Alternative guest token generation without Superset API
Generate guest token directly using JWT for Superset 3.0+
"""
import time
import jwt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_safe
from django.conf import settings


@require_safe
def generate_guest_token_direct(request, dashboard_id: str):
    """
    Generate guest token directly without calling Superset API
    This works for Superset 3.0+ when AUTH_ROLE_PUBLIC is configured
    """
    try:
        # Get Superset secret from environment or settings
        # This must match GUEST_TOKEN_JWT_SECRET in superset_config.py
        superset_secret = settings.SUPERSET_SECRET_KEY if hasattr(settings, 'SUPERSET_SECRET_KEY') else 'your_secret_key_change_this_in_production'

        # Prepare guest token payload
        payload = {
            "user": {
                "username": "guest_user",
                "first_name": "Guest",
                "last_name": "User"
            },
            "resources": [
                {
                    "type": "dashboard",
                    "id": dashboard_id
                }
            ],
            "rls": [],  # Row Level Security rules (empty for public access)
            "iat": int(time.time()),  # Issued at
            "exp": int(time.time()) + 300,  # Expires in 5 minutes
            "type": "guest"
        }

        # Generate JWT token
        token = jwt.encode(
            payload,
            superset_secret,
            algorithm='HS256'
        )

        return HttpResponse(token)

    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "message": "Failed to generate guest token"
        }, status=500)
