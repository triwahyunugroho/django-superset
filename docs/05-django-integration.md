# Django + Superset Integration Guide

## Overview

Dokumentasi lengkap untuk mengintegrasikan Django dengan Apache Superset, termasuk:
- List dashboards dari Superset
- Embed dashboards dengan guest token
- Authentication management
- Permission control
- Frontend implementation

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Journey                         │
└─────────────────────────────────────────────────────────┘

User → Django App → Superset API
  ↓         ↓            ↓
Login   Service      Dashboards
        Account      Charts
         Token       Datasets
           ↓            ↓
        Guest       Dashboard
         Token       Data
           ↓            ↓
      Frontend ←  Embed SDK
```

### Components

1. **Django Backend**
   - SupersetService class (API client)
   - Views (list, detail, guest token generation)
   - Models (optional: cache dashboard metadata)

2. **Django Frontend**
   - Dashboard list page
   - Dashboard view/embed page
   - JavaScript for Superset SDK

3. **Superset**
   - REST API
   - Dashboard/chart data
   - Authentication

---

## Prerequisites

### Required

- Python 3.8+
- Django 3.2+
- Apache Superset 6.0.0+ (running)
- requests library
- python-dotenv (optional, for environment variables)

### Optional

- Redis (for caching)
- PostgreSQL (for Django database)

---

## Installation

### 1. Install Python Dependencies

```bash
pip install requests python-dotenv django
```

### 2. Setup Superset

```bash
# Option 1: Docker Compose (Development)
git clone https://github.com/apache/superset
cd superset
git checkout tags/5.0.0
docker compose -f docker-compose-image-tag.yml up

# Option 2: Production setup (see Superset docs)
```

### 3. Configure Superset

Edit `superset_config.py`:

```python
# Enable features
FEATURE_FLAGS = {
    'DASHBOARD_RBAC': True,
    'EMBEDDED_SUPERSET': True,
}

# Guest token configuration
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = "your-secret-key-change-this"
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# CORS (if Django on different domain)
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'origins': [
        'http://localhost:8000',
        'https://yourdomain.com'
    ]
}
```

### 4. Create Service Account in Superset

```bash
# Via Superset CLI
superset fab create-user \
  --username django_service_account \
  --firstname Django \
  --lastname Service \
  --email service@example.com \
  --password YOUR_SECURE_PASSWORD \
  --role Admin

# Or via UI: Settings > List Users > + Add
```

### 5. Configure Django

Create `.env` file:

```bash
# .env
SUPERSET_URL=http://localhost:8088
SUPERSET_SERVICE_USER=django_service_account
SUPERSET_SERVICE_PASSWORD=YOUR_SECURE_PASSWORD
```

Update `settings.py`:

```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Superset configuration
SUPERSET_CONFIG = {
    'base_url': os.getenv('SUPERSET_URL', 'http://localhost:8088'),
    'service_account_username': os.getenv('SUPERSET_SERVICE_USER'),
    'service_account_password': os.getenv('SUPERSET_SERVICE_PASSWORD'),
}

# Cache configuration (optional, but recommended)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## Implementation

### 1. SupersetService Class

Create `services/superset_service.py`:

```python
# services/superset_service.py
import requests
import logging
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SupersetService:
    """
    Service class untuk interact dengan Superset API
    """

    def __init__(self):
        self.base_url = settings.SUPERSET_CONFIG['base_url'].rstrip('/')
        self.service_username = settings.SUPERSET_CONFIG['service_account_username']
        self.service_password = settings.SUPERSET_CONFIG['service_account_password']
        self._token_cache_key = 'superset_service_token'

    # =====================================
    # Authentication
    # =====================================

    def get_service_token(self) -> str:
        """
        Get service account token (cached)
        Token ini HANYA untuk backend, tidak dikirim ke frontend
        """
        # Check cache first
        token = cache.get(self._token_cache_key)
        if token:
            return token

        # Login to get new token
        token = self._login()

        # Cache for 50 minutes (token expires in 1 hour)
        cache.set(self._token_cache_key, token, timeout=3000)

        return token

    def _login(self) -> str:
        """Login dengan service account"""
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
            return data['access_token']

        except requests.exceptions.RequestException as e:
            logger.error(f"Superset login failed: {e}")
            raise Exception(f"Failed to authenticate with Superset: {e}")

    def invalidate_token(self):
        """Invalidate cached token (force refresh)"""
        cache.delete(self._token_cache_key)

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers with service token"""
        token = self.get_service_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request dengan automatic token refresh on 401
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method, url, headers=headers, timeout=30, **kwargs
            )

            # If 401, token might be expired, try refresh once
            if response.status_code == 401:
                logger.warning("Got 401, refreshing token...")
                self.invalidate_token()
                headers = self._get_headers()
                response = requests.request(
                    method, url, headers=headers, timeout=30, **kwargs
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}, Response: {e.response.text}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    # =====================================
    # Dashboard Operations
    # =====================================

    def list_dashboards(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List all dashboards"""
        endpoint = "/api/v1/dashboard/"

        if filters:
            # Add query parameters for filtering
            # Example: filters={'published': True}
            pass

        data = self._make_request('GET', endpoint)
        return data.get('result', [])

    def get_dashboard(self, dashboard_id_or_uuid: str) -> Dict[str, Any]:
        """Get dashboard detail by ID or UUID"""
        endpoint = f"/api/v1/dashboard/{dashboard_id_or_uuid}"
        data = self._make_request('GET', endpoint)
        return data.get('result', {})

    def update_dashboard(self, dashboard_id: int, **kwargs) -> Dict[str, Any]:
        """Update dashboard"""
        endpoint = f"/api/v1/dashboard/{dashboard_id}"
        data = self._make_request('PUT', endpoint, json=kwargs)
        return data.get('result', {})

    def delete_dashboard(self, dashboard_id: int) -> bool:
        """Delete dashboard"""
        endpoint = f"/api/v1/dashboard/{dashboard_id}"
        try:
            self._make_request('DELETE', endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete dashboard: {e}")
            return False

    # =====================================
    # Chart Operations
    # =====================================

    def list_charts(self) -> List[Dict]:
        """List all charts"""
        endpoint = "/api/v1/chart/"
        data = self._make_request('GET', endpoint)
        return data.get('result', [])

    def get_chart(self, chart_id: int) -> Dict[str, Any]:
        """Get chart detail"""
        endpoint = f"/api/v1/chart/{chart_id}"
        data = self._make_request('GET', endpoint)
        return data.get('result', {})

    def get_chart_data(self, chart_id: int) -> Dict[str, Any]:
        """Get chart data (actual query results)"""
        endpoint = f"/api/v1/chart/{chart_id}/data/"
        data = self._make_request('GET', endpoint)
        return data.get('result', {})

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
        Create guest token untuk embed dashboard

        Args:
            dashboard_uuid: UUID dashboard (bukan integer ID!)
            user_info: User info untuk audit {username, first_name, last_name}
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
            if e.response.status_code == 403:
                raise Exception(
                    "Dashboard not accessible via guest token. "
                    "Ensure dashboard is Published and has Public role."
                )
            raise

    def create_guest_token_for_user(
        self,
        dashboard_uuid: str,
        django_user
    ) -> str:
        """
        Create guest token dengan Django user context

        Args:
            dashboard_uuid: UUID dashboard
            django_user: Django User object

        Returns:
            Guest token string
        """
        user_info = {
            "username": django_user.username,
            "first_name": django_user.first_name or django_user.username,
            "last_name": django_user.last_name or ""
        }

        # Optional: Add RLS based on user attributes
        rls_rules = []
        if hasattr(django_user, 'profile'):
            # Example: Filter by department
            if hasattr(django_user.profile, 'department'):
                department = django_user.profile.department
                rls_rules.append({
                    "clause": f"department = '{department}'"
                })

        return self.create_guest_token(
            dashboard_uuid=dashboard_uuid,
            user_info=user_info,
            rls_rules=rls_rules
        )

    # =====================================
    # Visibility & Permissions
    # =====================================

    def get_dashboard_visibility_info(self, dashboard_id_or_uuid: str) -> Dict:
        """
        Get comprehensive visibility info for dashboard
        """
        dashboard = self.get_dashboard(dashboard_id_or_uuid)

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
            'id': dashboard['id'],
            'uuid': dashboard['uuid'],
            'title': dashboard['dashboard_title'],
            'published': is_published,
            'roles': role_names,
            'has_public_role': has_public_role,
            'guest_token_accessible': guest_token_accessible,
            'reason': reason,
            'owners': [o['username'] for o in dashboard.get('owners', [])],
            'thumbnail_url': dashboard.get('thumbnail_url'),
            'url': dashboard.get('url')
        }

    def can_create_guest_token_for(self, dashboard_uuid: str) -> tuple:
        """
        Check if guest token can be created for dashboard

        Returns:
            (can_create: bool, reason: str)
        """
        try:
            info = self.get_dashboard_visibility_info(dashboard_uuid)

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

    def set_dashboard_public(self, dashboard_id: int) -> bool:
        """
        Make dashboard public:
        - Set published = True
        - Add Public role (if DASHBOARD_RBAC enabled)

        Args:
            dashboard_id: Dashboard ID (integer)

        Returns:
            Success status
        """
        try:
            # Get current dashboard
            dashboard = self.get_dashboard(dashboard_id)

            # Update payload
            payload = {
                "published": True
            }

            # Get Public role
            public_role = self._get_public_role()
            if public_role:
                roles = dashboard.get('roles', [])
                # Check if Public already in list
                has_public = any(
                    r['name'].lower() == 'public' for r in roles
                )

                if not has_public:
                    roles.append(public_role)
                    payload['roles'] = roles

            # Update dashboard
            self.update_dashboard(dashboard_id, **payload)
            logger.info(f"Dashboard {dashboard_id} is now public")
            return True

        except Exception as e:
            logger.error(f"Failed to make dashboard public: {e}")
            return False

    def _get_public_role(self) -> Optional[Dict]:
        """Get Public role info"""
        try:
            endpoint = "/api/v1/security/roles/"
            params = {
                'q': '(filters:!((col:name,opr:eq,value:Public)))'
            }

            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()

            results = response.json().get('result', [])
            if results:
                return results[0]

        except Exception as e:
            logger.warning(f"Failed to get Public role: {e}")

        return None

    # =====================================
    # Helper Methods
    # =====================================

    def format_dashboard_for_frontend(self, dashboard: Dict) -> Dict:
        """
        Format dashboard data untuk frontend consumption
        """
        return {
            'id': dashboard['id'],
            'uuid': dashboard['uuid'],
            'title': dashboard['dashboard_title'],
            'url': dashboard.get('url'),
            'published': dashboard.get('published', False),
            'thumbnail_url': dashboard.get('thumbnail_url'),
            'owners': [
                {
                    'username': o['username'],
                    'name': f"{o.get('first_name', '')} {o.get('last_name', '')}".strip()
                }
                for o in dashboard.get('owners', [])
            ],
            'roles': [r['name'] for r in dashboard.get('roles', [])],
            'charts_count': len(dashboard.get('slices', [])),
            'changed_on': dashboard.get('changed_on'),
        }
```

### 2. Django Views

Create `views.py`:

```python
# views.py
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from services.superset_service import SupersetService

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def dashboard_list(request):
    """
    List all dashboards from Superset
    """
    try:
        superset = SupersetService()
        dashboards = superset.list_dashboards()

        # Format for frontend
        formatted_dashboards = [
            superset.format_dashboard_for_frontend(d)
            for d in dashboards
        ]

        # Optional: Filter based on user permissions
        # You can add custom logic here

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


@login_required
def dashboard_list_page(request):
    """
    Page untuk display dashboard list
    """
    context = {
        'superset_url': settings.SUPERSET_CONFIG['base_url']
    }
    return render(request, 'superset/dashboard_list.html', context)


@login_required
def dashboard_view(request, dashboard_uuid):
    """
    Page untuk view embedded dashboard
    """
    try:
        superset = SupersetService()

        # Get dashboard info
        info = superset.get_dashboard_visibility_info(dashboard_uuid)

        # Check if accessible
        can_access, reason = superset.can_create_guest_token_for(dashboard_uuid)

        if can_access is False:
            return render(request, 'superset/dashboard_error.html', {
                'error': reason,
                'dashboard_title': info.get('title', 'Unknown Dashboard')
            })

        context = {
            'dashboard_uuid': dashboard_uuid,
            'dashboard_title': info['title'],
            'superset_url': settings.SUPERSET_CONFIG['base_url'],
            'can_access': can_access,
            'reason': reason
        }

        return render(request, 'superset/dashboard_view.html', context)

    except Exception as e:
        logger.error(f"Failed to load dashboard view: {e}")
        return render(request, 'superset/dashboard_error.html', {
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def get_guest_token(request):
    """
    API endpoint untuk frontend request guest token
    Called by Superset Embedded SDK
    """
    try:
        data = json.loads(request.body)
        dashboard_uuid = data.get('dashboard_uuid')

        if not dashboard_uuid:
            return JsonResponse({
                'success': False,
                'error': 'dashboard_uuid required'
            }, status=400)

        # Check if user allowed to access this dashboard
        # Add your permission logic here if needed

        # Create guest token
        superset = SupersetService()
        guest_token = superset.create_guest_token_for_user(
            dashboard_uuid=dashboard_uuid,
            django_user=request.user
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


@login_required
@require_http_methods(["GET"])
def dashboard_info(request, dashboard_uuid):
    """
    Get dashboard visibility info
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
```

### 3. URLs

Create `urls.py`:

```python
# urls.py
from django.urls import path
from . import views

app_name = 'superset'

urlpatterns = [
    # Pages
    path('dashboards/', views.dashboard_list_page, name='dashboard_list_page'),
    path('dashboard/<str:dashboard_uuid>/', views.dashboard_view, name='dashboard_view'),

    # API endpoints
    path('api/dashboards/', views.dashboard_list, name='dashboard_list_api'),
    path('api/dashboard/<str:dashboard_uuid>/', views.dashboard_info, name='dashboard_info'),
    path('api/guest-token/', views.get_guest_token, name='get_guest_token'),
]
```

Include in main `urls.py`:

```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('superset/', include('superset_integration.urls')),
]
```

### 4. Templates

Create `templates/superset/dashboard_list.html`:

```html
<!-- templates/superset/dashboard_list.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h1>Superset Dashboards</h1>

    <div id="loading">Loading dashboards...</div>
    <div id="error" class="alert alert-danger" style="display: none;"></div>

    <div id="dashboard-grid" class="row g-4">
        <!-- Dashboard cards will be inserted here -->
    </div>
</div>

<style>
    .dashboard-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        cursor: pointer;
        transition: box-shadow 0.3s;
        height: 100%;
    }

    .dashboard-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .dashboard-thumbnail {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 4px;
        background: #f5f5f5;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #999;
    }

    .badge {
        font-size: 0.75rem;
        margin-right: 5px;
    }
</style>

<script>
    async function loadDashboards() {
        try {
            const response = await fetch('/superset/api/dashboards/');
            const data = await response.json();

            document.getElementById('loading').style.display = 'none';

            if (!data.success) {
                showError(data.error);
                return;
            }

            renderDashboards(data.dashboards);

        } catch (error) {
            document.getElementById('loading').style.display = 'none';
            showError('Failed to load dashboards: ' + error.message);
        }
    }

    function renderDashboards(dashboards) {
        const grid = document.getElementById('dashboard-grid');
        grid.innerHTML = '';

        if (dashboards.length === 0) {
            grid.innerHTML = '<p class="col-12">No dashboards found.</p>';
            return;
        }

        dashboards.forEach(dashboard => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4';

            col.innerHTML = `
                <div class="dashboard-card" onclick="viewDashboard('${dashboard.uuid}')">
                    ${dashboard.thumbnail_url ?
                        `<img src="{{ superset_url }}${dashboard.thumbnail_url}" class="dashboard-thumbnail" alt="${dashboard.title}" />` :
                        '<div class="dashboard-thumbnail">No Preview</div>'
                    }

                    <h5 class="mt-3">${dashboard.title}</h5>

                    <div class="mb-2">
                        ${dashboard.published ?
                            '<span class="badge bg-success">Published</span>' :
                            '<span class="badge bg-warning">Draft</span>'
                        }
                        ${dashboard.roles.includes('Public') ?
                            '<span class="badge bg-info">Public</span>' :
                            '<span class="badge bg-secondary">Internal</span>'
                        }
                    </div>

                    <small class="text-muted">
                        ${dashboard.charts_count} charts •
                        By ${dashboard.owners.map(o => o.name || o.username).join(', ')}
                    </small>
                </div>
            `;

            grid.appendChild(col);
        });
    }

    function viewDashboard(uuid) {
        window.location.href = `/superset/dashboard/${uuid}/`;
    }

    function showError(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    // Load dashboards on page load
    loadDashboards();
</script>
{% endblock %}
```

Create `templates/superset/dashboard_view.html`:

```html
<!-- templates/superset/dashboard_view.html -->
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center my-3">
                <h2>{{ dashboard_title }}</h2>
                <a href="{% url 'superset:dashboard_list_page' %}" class="btn btn-secondary">
                    Back to Dashboards
                </a>
            </div>

            <div id="loading" class="text-center my-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Loading dashboard...</p>
            </div>

            <div id="error" class="alert alert-danger" style="display: none;"></div>

            <div id="superset-container" style="width: 100%; height: 800px;"></div>
        </div>
    </div>
</div>

<script src="https://unpkg.com/@superset-ui/embedded-sdk@0.1.0-alpha.10/bundle/index.js"></script>
<script>
    const dashboardUuid = "{{ dashboard_uuid }}";
    const supersetUrl = "{{ superset_url }}";

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Fetch guest token from Django backend
    async function fetchGuestToken() {
        try {
            const response = await fetch('/superset/api/guest-token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    dashboard_uuid: dashboardUuid
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error);
            }

            return data.guest_token;

        } catch (error) {
            console.error('Failed to fetch guest token:', error);
            showError('Failed to load dashboard: ' + error.message);
            throw error;
        }
    }

    // Embed dashboard
    async function embedDashboard() {
        try {
            document.getElementById('loading').style.display = 'block';

            await supersetEmbeddedSdk.embedDashboard({
                id: dashboardUuid,
                supersetDomain: supersetUrl,
                mountPoint: document.getElementById('superset-container'),
                fetchGuestToken: fetchGuestToken,
                dashboardUiConfig: {
                    hideTitle: false,
                    hideChartControls: false,
                    hideTab: false,
                    filters: {
                        expanded: true,
                    },
                }
            });

            document.getElementById('loading').style.display = 'none';
            console.log('Dashboard embedded successfully');

        } catch (error) {
            document.getElementById('loading').style.display = 'none';
            console.error('Failed to embed dashboard:', error);
            showError('Failed to load dashboard: ' + error.message);
        }
    }

    function showError(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    // Embed dashboard on page load
    embedDashboard();
</script>
{% endblock %}
```

Create `templates/superset/dashboard_error.html`:

```html
<!-- templates/superset/dashboard_error.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="alert alert-danger">
        <h4>Cannot Load Dashboard</h4>
        <p>{{ error }}</p>

        {% if dashboard_title %}
        <p><strong>Dashboard:</strong> {{ dashboard_title }}</p>
        {% endif %}

        <hr>

        <p>Possible reasons:</p>
        <ul>
            <li>Dashboard is in Draft mode</li>
            <li>Dashboard is not accessible to Public role</li>
            <li>You don't have permission to view this dashboard</li>
        </ul>

        <a href="{% url 'superset:dashboard_list_page' %}" class="btn btn-primary">
            Back to Dashboard List
        </a>
    </div>
</div>
{% endblock %}
```

---

## Testing

### 1. Test Service Account Connection

```python
# Django shell
python manage.py shell

from services.superset_service import SupersetService

superset = SupersetService()

# Test login
token = superset.get_service_token()
print(f"Token: {token[:50]}...")

# Test list dashboards
dashboards = superset.list_dashboards()
print(f"Found {len(dashboards)} dashboards")

for d in dashboards[:3]:
    print(f"- {d['dashboard_title']} (ID: {d['id']}, UUID: {d['uuid']})")
```

### 2. Test Guest Token Creation

```python
# Django shell
from services.superset_service import SupersetService

superset = SupersetService()

# Get a dashboard UUID
dashboards = superset.list_dashboards()
dashboard_uuid = dashboards[0]['uuid']

# Try to create guest token
try:
    token = superset.create_guest_token(dashboard_uuid)
    print(f"Guest token created: {token[:50]}...")
except Exception as e:
    print(f"Failed: {e}")
```

### 3. Test via Browser

1. Start Django dev server:
```bash
python manage.py runserver
```

2. Navigate to:
```
http://localhost:8000/superset/dashboards/
```

3. Should see list of dashboards

4. Click a dashboard to view embedded version

---

## Deployment

### Production Checklist

1. **Environment Variables**
```bash
# Use strong passwords
SUPERSET_SERVICE_PASSWORD=<strong-random-password>

# Use production URLs
SUPERSET_URL=https://superset.yourdomain.com

# Set DEBUG=False
DEBUG=False
```

2. **Superset Configuration**
```python
# superset_config.py

# Strong secret keys
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')
GUEST_TOKEN_JWT_SECRET = os.environ.get('GUEST_TOKEN_SECRET')

# Production CORS
CORS_OPTIONS = {
    'origins': ['https://yourdomain.com']
}

# Enable caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://redis:6379/1'
}
```

3. **Django Configuration**
```python
# settings.py

# Use Redis for caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

4. **Logging**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/superset_integration.log',
        },
    },
    'loggers': {
        'services.superset_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Advanced Topics

### Caching Dashboard Metadata

```python
# models.py
from django.db import models

class CachedDashboard(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    published = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    metadata = models.JSONField()
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_synced']

# Management command to sync
# management/commands/sync_superset_dashboards.py
from django.core.management.base import BaseCommand
from services.superset_service import SupersetService
from myapp.models import CachedDashboard

class Command(BaseCommand):
    help = 'Sync dashboards from Superset'

    def handle(self, *args, **options):
        superset = SupersetService()
        dashboards = superset.list_dashboards()

        for dashboard in dashboards:
            info = superset.get_dashboard_visibility_info(dashboard['uuid'])

            CachedDashboard.objects.update_or_create(
                uuid=dashboard['uuid'],
                defaults={
                    'title': info['title'],
                    'published': info['published'],
                    'is_public': info['guest_token_accessible'] or False,
                    'metadata': info
                }
            )

        self.stdout.write(
            self.style.SUCCESS(f'Synced {len(dashboards)} dashboards')
        )
```

### Permission-based Filtering

```python
# views.py
def dashboard_list(request):
    superset = SupersetService()
    all_dashboards = superset.list_dashboards()

    # Filter based on Django user
    filtered = []
    for dashboard in all_dashboards:
        # Custom permission logic
        if user_can_view_dashboard(request.user, dashboard):
            filtered.append(dashboard)

    return JsonResponse({
        'dashboards': filtered
    })

def user_can_view_dashboard(user, dashboard):
    """Custom permission logic"""
    # Example: Only show published dashboards to non-staff
    if not user.is_staff and not dashboard.get('published'):
        return False

    # Example: Filter by user groups
    if hasattr(user, 'profile'):
        user_department = user.profile.department
        dashboard_tags = dashboard.get('tags', [])

        if user_department not in dashboard_tags:
            return False

    return True
```

---

## Troubleshooting

### Common Issues

**1. Token Authentication Failed**
```
Error: 401 Unauthorized

Solution:
- Check service account credentials in .env
- Verify user exists and is active in Superset
- Try logging in manually to Superset UI
```

**2. Guest Token 403 Forbidden**
```
Error: 403 when creating guest token

Solution:
- Ensure dashboard is Published
- Add Public role to dashboard
- Enable EMBEDDED_SUPERSET feature flag
- Check service account has can_grant_guest_token permission
```

**3. CORS Error in Browser**
```
Error: CORS policy blocked

Solution:
# superset_config.py
ENABLE_CORS = True
CORS_OPTIONS = {
    'origins': ['http://localhost:8000']
}
```

**4. Dashboard Won't Load**
```
Error: Dashboard loads but shows blank/error

Solution:
- Check browser console for errors
- Verify guest token is being fetched
- Check dashboard UUID is correct
- Try accessing dashboard directly in Superset UI
```

---

## Next Steps

- Setup monitoring and logging
- Implement caching strategy
- Add user analytics
- Create custom Django admin interface
- Setup automated dashboard sync
- Implement advanced RLS rules

---

## Resources

- [Apache Superset Documentation](https://superset.apache.org/docs/6.0.0/)
- [Superset API](https://superset.apache.org/docs/6.0.0/api)
- [Embedded SDK](https://www.npmjs.com/package/@superset-ui/embedded-sdk)
- [Django Documentation](https://docs.djangoproject.com/)

---

## Support

For issues or questions:
- Check [Superset GitHub Issues](https://github.com/apache/superset/issues)
- Join [Superset Slack](https://apache-superset.slack.com/)
- Review this documentation
