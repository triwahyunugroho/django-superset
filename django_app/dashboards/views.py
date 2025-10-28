"""
Views for Superset Dashboard integration.
Allows public access to dashboards without authentication.
"""

import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from services.superset_service import SupersetService

logger = logging.getLogger(__name__)


def home(request):
    """Home page - redirect to dashboard list"""
    return render(request, 'dashboards/home.html', {
        'superset_url': settings.SUPERSET_CONFIG['base_url']
    })


@require_http_methods(["GET"])
def dashboard_list_page(request):
    """
    Page to display list of public dashboards
    Accessible without login
    """
    context = {
        'superset_url': settings.SUPERSET_CONFIG['base_url']
    }
    return render(request, 'dashboards/dashboard_list.html', context)


@require_http_methods(["GET"])
def dashboard_list_api(request):
    """
    API endpoint to get list of public dashboards
    Returns only dashboards that have Public role (accessible via guest token)
    """
    try:
        superset = SupersetService()

        # Get only public dashboards (Published + has Public role)
        public_dashboards = superset.list_public_dashboards()

        # Format for frontend
        formatted_dashboards = [
            superset.format_dashboard_for_frontend(d)
            for d in public_dashboards
        ]

        return JsonResponse({
            'success': True,
            'dashboards': formatted_dashboards,
            'count': len(formatted_dashboards)
        })

    except Exception as e:
        logger.error(f"Failed to list dashboards: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def dashboard_view(request, dashboard_uuid):
    """
    Page to view embedded dashboard
    Accessible without login for public dashboards
    """
    try:
        superset = SupersetService()

        # Get dashboard info
        info = superset.get_dashboard_visibility_info(dashboard_uuid)

        if 'error' in info:
            return render(request, 'dashboards/dashboard_error.html', {
                'error': info['error'],
                'dashboard_title': 'Unknown Dashboard'
            })

        # Check if accessible via guest token
        can_access, reason = superset.can_create_guest_token_for(dashboard_uuid)

        if can_access is False:
            return render(request, 'dashboards/dashboard_error.html', {
                'error': reason,
                'dashboard_title': info.get('title', 'Unknown Dashboard'),
                'dashboard_info': info
            })

        context = {
            'dashboard_uuid': dashboard_uuid,
            'dashboard_title': info['title'],
            'superset_url': settings.SUPERSET_CONFIG['base_url'],
            'can_access': can_access,
            'reason': reason,
            'dashboard_info': info
        }

        return render(request, 'dashboards/dashboard_view.html', context)

    except Exception as e:
        logger.error(f"Failed to load dashboard view: {e}")
        return render(request, 'dashboards/dashboard_error.html', {
            'error': str(e),
            'dashboard_title': 'Error'
        })


@csrf_exempt  # Allow public access without CSRF (can add CORS headers if needed)
@require_http_methods(["POST"])
def get_guest_token(request):
    """
    API endpoint to generate guest token for dashboard embedding
    Called by Superset Embedded SDK
    Public endpoint - no authentication required
    """
    try:
        data = json.loads(request.body)
        dashboard_uuid = data.get('dashboard_uuid')

        if not dashboard_uuid:
            return JsonResponse({
                'success': False,
                'error': 'dashboard_uuid required'
            }, status=400)

        # Check if dashboard is accessible
        superset = SupersetService()
        can_access, reason = superset.can_create_guest_token_for(dashboard_uuid)

        if can_access is False:
            return JsonResponse({
                'success': False,
                'error': reason
            }, status=403)

        # Create guest token with generic guest user info
        guest_token = superset.create_guest_token(
            dashboard_uuid=dashboard_uuid,
            user_info={
                "username": "public_guest",
                "first_name": "Public",
                "last_name": "Guest"
            }
        )

        return JsonResponse({
            'success': True,
            'guest_token': guest_token
        })

    except Exception as e:
        logger.error(f"Failed to create guest token: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def dashboard_info_api(request, dashboard_uuid):
    """
    API endpoint to get dashboard visibility information
    """
    try:
        superset = SupersetService()
        info = superset.get_dashboard_visibility_info(dashboard_uuid)

        return JsonResponse({
            'success': True,
            'dashboard': info
        })

    except Exception as e:
        logger.error(f"Failed to get dashboard info: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
