"""
Superset Service for Django integration.
Handles all interactions with Superset API.
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SupersetService:
    """Service class to interact with Superset API"""

    def __init__(self):
        self.base_url = settings.SUPERSET_CONFIG['base_url'].rstrip('/')
        self.service_username = settings.SUPERSET_CONFIG['service_account_username']
        self.service_password = settings.SUPERSET_CONFIG['service_account_password']
        self._token_cache_key = 'superset_service_token'
        self._csrf_cache_key = 'superset_csrf_token'

    # =====================================
    # Authentication
    # =====================================

    def get_service_token(self) -> str:
        """
        Get service account token (cached)
        Token is ONLY for backend use, never sent to frontend
        """
        # Check cache first
        token = cache.get(self._token_cache_key)
        if token:
            logger.debug("Using cached service token")
            return token

        # Login to get new token
        logger.info("Fetching new service token")
        token = self._login()

        # Cache for 50 minutes (token expires in 1 hour)
        cache.set(self._token_cache_key, token, timeout=3000)

        return token

    def _login(self) -> str:
        """Login with service account"""
        url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": self.service_username,
            "password": self.service_password,
            "provider": "db",
            "refresh": True
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully logged in as {self.service_username}")
            return data['access_token']

        except requests.exceptions.RequestException as e:
            logger.error(f"Superset login failed: {e}")
            raise Exception(f"Failed to authenticate with Superset: {e}")

    def invalidate_token(self):
        """Invalidate cached token (force refresh)"""
        cache.delete(self._token_cache_key)
        logger.info("Service token cache invalidated")

    def get_csrf_token(self) -> str:
        """
        Get CSRF token (cached)
        Required for POST/PUT/DELETE requests
        """
        # Check cache first
        csrf = cache.get(self._csrf_cache_key)
        if csrf:
            logger.debug("Using cached CSRF token")
            return csrf

        # Fetch new CSRF token
        logger.info("Fetching new CSRF token")
        url = f"{self.base_url}/api/v1/security/csrf_token/"
        token = self.get_service_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            csrf = data.get('result')

            # Cache for 50 minutes
            cache.set(self._csrf_cache_key, csrf, timeout=3000)

            return csrf

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get CSRF token: {e}")
            raise Exception(f"Failed to get CSRF token: {e}")

    def _get_headers(self, include_csrf: bool = False) -> Dict[str, str]:
        """Get authorization headers with service token"""
        token = self.get_service_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        if include_csrf:
            csrf = self.get_csrf_token()
            headers["X-CSRFToken"] = csrf
            headers["Referer"] = self.base_url

        return headers

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request with automatic token refresh on 401
        Automatically includes CSRF token for POST/PUT/PATCH/DELETE
        """
        url = f"{self.base_url}{endpoint}"

        # Include CSRF for mutating requests
        needs_csrf = method.upper() in ['POST', 'PUT', 'PATCH', 'DELETE']
        headers = self._get_headers(include_csrf=needs_csrf)

        try:
            response = requests.request(
                method, url, headers=headers, timeout=30, **kwargs
            )

            # If 401, token might be expired, try refresh once
            if response.status_code == 401:
                logger.warning("Got 401, refreshing token...")
                self.invalidate_token()
                headers = self._get_headers(include_csrf=needs_csrf)
                response = requests.request(
                    method, url, headers=headers, timeout=30, **kwargs
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}, Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    # =====================================
    # Dashboard Operations
    # =====================================

    def list_dashboards(self, published_only: bool = True) -> List[Dict]:
        """
        List all dashboards

        Args:
            published_only: If True, only return published dashboards

        Returns:
            List of dashboard objects
        """
        endpoint = "/api/v1/dashboard/"

        try:
            data = self._make_request('GET', endpoint)
            dashboards = data.get('result', [])

            if published_only:
                dashboards = [d for d in dashboards if d.get('published', False)]

            logger.info(f"Retrieved {len(dashboards)} dashboards")
            return dashboards

        except Exception as e:
            logger.error(f"Failed to list dashboards: {e}")
            return []

    def get_dashboard(self, dashboard_id_or_uuid: str) -> Optional[Dict[str, Any]]:
        """Get dashboard detail by ID or UUID"""
        endpoint = f"/api/v1/dashboard/{dashboard_id_or_uuid}"

        try:
            data = self._make_request('GET', endpoint)
            dashboard = data.get('result', {})
            logger.info(f"Retrieved dashboard: {dashboard.get('dashboard_title')}")
            return dashboard

        except Exception as e:
            logger.error(f"Failed to get dashboard {dashboard_id_or_uuid}: {e}")
            return None

    def get_dashboard_visibility_info(self, dashboard_id_or_uuid: str) -> Dict:
        """
        Get comprehensive visibility info for dashboard

        Returns:
            Dict with visibility information including:
            - published status
            - roles
            - guest_token_accessible
            - reason
        """
        dashboard = self.get_dashboard(dashboard_id_or_uuid)

        if not dashboard:
            return {
                'error': 'Dashboard not found',
                'guest_token_accessible': False
            }

        is_published = dashboard.get('published', False)
        roles = dashboard.get('roles', [])
        role_names = [r['name'] for r in roles]
        has_public_role = 'Public' in role_names or 'public' in role_names

        # Determine guest token accessibility
        guest_token_accessible = False
        reason = ""

        if not is_published:
            reason = "Dashboard is in Draft status"
        elif has_public_role:
            guest_token_accessible = True
            reason = "Dashboard has Public role access"
        elif not roles:
            reason = "Dashboard has no roles (depends on dataset permissions)"
            guest_token_accessible = None  # Unknown
        else:
            reason = "Dashboard does not have Public role access"

        return {
            'id': dashboard.get('id'),
            'uuid': dashboard.get('uuid'),
            'title': dashboard.get('dashboard_title'),
            'published': is_published,
            'roles': role_names,
            'has_public_role': has_public_role,
            'guest_token_accessible': guest_token_accessible,
            'reason': reason,
            'owners': [o.get('username', 'unknown') for o in dashboard.get('owners', [])],
            'thumbnail_url': dashboard.get('thumbnail_url'),
            'url': dashboard.get('url')
        }

    def list_public_dashboards(self) -> List[Dict]:
        """
        List only dashboards that are accessible via guest token
        (Published + has Public role)
        """
        all_dashboards = self.list_dashboards(published_only=True)
        public_dashboards = []

        for dashboard in all_dashboards:
            roles = dashboard.get('roles', [])
            role_names = [r['name'] for r in roles]

            # Check if Public role is assigned
            if 'Public' in role_names or 'public' in role_names:
                public_dashboards.append(dashboard)

        logger.info(f"Found {len(public_dashboards)} public dashboards")
        return public_dashboards

    # =====================================
    # Guest Token Operations
    # =====================================

    def create_guest_token(
        self,
        dashboard_uuid: str,
        user_info: Optional[Dict] = None,
        rls_rules: Optional[List[Dict]] = None
    ) -> str:
        """
        Create guest token for embedding dashboard

        Args:
            dashboard_uuid: UUID of the dashboard (not integer ID!)
            user_info: User info for audit {username, first_name, last_name}
            rls_rules: Row Level Security rules [{clause: "..."}]

        Returns:
            Guest token string

        Raises:
            Exception: If dashboard not accessible or other errors
        """
        # Default user info
        if user_info is None:
            user_info = {
                "username": "guest",
                "first_name": "Guest",
                "last_name": "User"
            }

        # Payload
        payload = {
            "user": user_info,
            "resources": [
                {
                    "type": "dashboard",
                    "id": dashboard_uuid
                }
            ],
            "rls": rls_rules or []
        }

        # Create guest token
        endpoint = "/api/v1/security/guest_token/"

        try:
            data = self._make_request('POST', endpoint, json=payload)
            guest_token = data.get('token')

            if not guest_token:
                raise Exception("No guest token returned")

            logger.info(f"Created guest token for dashboard {dashboard_uuid}")
            return guest_token

        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 403:
                raise Exception(
                    "Dashboard not accessible via guest token. "
                    "Ensure dashboard is Published and has Public role."
                )
            raise

    def can_create_guest_token_for(self, dashboard_uuid: str) -> tuple:
        """
        Check if guest token can be created for dashboard

        Returns:
            (can_create: bool, reason: str)
        """
        try:
            info = self.get_dashboard_visibility_info(dashboard_uuid)

            if 'error' in info:
                return False, info['error']

            if not info['published']:
                return False, "Dashboard is in Draft mode"

            if info['guest_token_accessible'] is True:
                return True, "Dashboard is accessible via guest token"

            if info['guest_token_accessible'] is None:
                return None, "Unknown (depends on dataset permissions)"

            return False, "Dashboard does not have Public role access"

        except Exception as e:
            logger.error(f"Failed to check dashboard accessibility: {e}")
            return False, str(e)

    # =====================================
    # Helper Methods
    # =====================================

    def format_dashboard_for_frontend(self, dashboard: Dict) -> Dict:
        """
        Format dashboard data for frontend consumption
        """
        roles = dashboard.get('roles', [])
        role_names = [r['name'] for r in roles]
        has_public_role = 'Public' in role_names or 'public' in role_names

        return {
            'id': dashboard.get('id'),
            'uuid': dashboard.get('uuid'),
            'title': dashboard.get('dashboard_title', 'Untitled Dashboard'),
            'url': dashboard.get('url'),
            'published': dashboard.get('published', False),
            'thumbnail_url': dashboard.get('thumbnail_url'),
            'owners': [
                {
                    'username': o.get('username'),
                    'name': f"{o.get('first_name', '')} {o.get('last_name', '')}".strip() or o.get('username')
                }
                for o in dashboard.get('owners', [])
            ],
            'roles': role_names,
            'is_public': has_public_role,
            'charts_count': len(dashboard.get('slices', [])),
            'changed_on': dashboard.get('changed_on'),
        }
