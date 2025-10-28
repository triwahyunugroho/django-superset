# Authentication & Token Management

## Overview

Superset mendukung berbagai metode autentikasi, tapi untuk integrasi dengan aplikasi external (seperti Django), ada 2 jenis token yang perlu dipahami:

1. **Service Account Token**: Regular access token untuk backend operations
2. **Guest Token**: Temporary token untuk embedding dashboards

## Service Account Token

### Apa itu Service Account Token?

**Service Account Token** adalah access token yang didapat dari akun khusus (bukan user biasa) yang digunakan untuk komunikasi **server-to-server** atau **machine-to-machine**.

### Karakteristik

| Aspek | Detail |
|-------|--------|
| **Dibuat oleh** | Login dengan service account credentials |
| **Digunakan oleh** | Backend/server application (Django) |
| **Digunakan untuk** | API calls (list, create, update, delete) |
| **Scope** | Full sesuai role (Admin/Alpha/Gamma) |
| **Lifetime** | ~1 jam (configurable) |
| **Di-cache?** | Ya (recommended) |
| **Sent to frontend?** | ❌ NO - stays in backend |

### Membuat Service Account

#### 1. Buat User di Superset

Via UI:
```
1. Login sebagai Admin
2. Settings > List Users
3. Klik "+ Add"
4. Isi form:
   - Username: django_service_account
   - First Name: Django
   - Last Name: Service
   - Email: service@yourdomain.com
   - Role: Admin atau Alpha
   - Active: Yes
5. Save
```

Via CLI (jika akses ke Superset container):
```bash
superset fab create-user \
  --username django_service_account \
  --firstname Django \
  --lastname Service \
  --email service@example.com \
  --password YOUR_SECURE_PASSWORD \
  --role Admin
```

#### 2. Pilih Role yang Sesuai

**Admin Role**:
- Full access ke semua resources
- Bisa manage users
- Gunakan jika Django perlu full control

**Alpha Role**:
- Access ke semua data sources
- Tidak bisa manage users
- Lebih aman untuk production

**Custom Role**:
- Buat role khusus dengan permissions spesifik
- Contoh: "API Reader" - hanya read access

#### 3. Store Credentials Securely

```python
# .env file
SUPERSET_URL=http://localhost:8088
SUPERSET_SERVICE_USER=django_service_account
SUPERSET_SERVICE_PASSWORD=very_secure_random_password_here
```

```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SUPERSET_CONFIG = {
    'base_url': os.getenv('SUPERSET_URL'),
    'service_account_username': os.getenv('SUPERSET_SERVICE_USER'),
    'service_account_password': os.getenv('SUPERSET_SERVICE_PASSWORD'),
}
```

### Menggunakan Service Account Token

```python
# services/superset_service.py
import requests
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta

class SupersetService:
    def __init__(self):
        self.base_url = settings.SUPERSET_CONFIG['base_url']
        self.service_username = settings.SUPERSET_CONFIG['service_account_username']
        self.service_password = settings.SUPERSET_CONFIG['service_account_password']

    def get_service_token(self):
        """
        Get service account token
        Token ini digunakan di backend, TIDAK dikirim ke frontend
        """
        # Check cache first
        cache_key = 'superset_service_token'
        token = cache.get(cache_key)

        if token:
            return token

        # Login dengan service account
        url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": self.service_username,
            "password": self.service_password,
            "provider": "db",
            "refresh": True
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        token = response.json()['access_token']

        # Cache untuk 50 menit (token expire dalam 1 jam)
        cache.set(cache_key, token, timeout=3000)

        return token

    def list_dashboards(self):
        """Use service token untuk list dashboards"""
        token = self.get_service_token()
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{self.base_url}/api/v1/dashboard/",
            headers=headers
        )
        response.raise_for_status()

        return response.json()['result']
```

### Use Cases

✅ **Kapan Pakai Service Account Token:**

1. **List resources** (dashboards, charts, datasets)
2. **Create/Update/Delete** resources via API
3. **Get dashboard metadata**
4. **Execute SQL queries** via API
5. **Create guest tokens** (explained below)
6. **Manage permissions** programmatically

❌ **Jangan Pakai Untuk:**

1. Embed dashboards di frontend (use guest token)
2. Store di client-side code
3. Send ke browser/frontend

---

## Guest Token

### Apa itu Guest Token?

**Guest Token** adalah token sementara yang digunakan untuk **embed dashboard** di aplikasi external tanpa perlu user login ke Superset.

### Karakteristik

| Aspek | Detail |
|-------|--------|
| **Dibuat oleh** | Backend (using service account token) |
| **Digunakan oleh** | Frontend/browser |
| **Digunakan untuk** | View specific dashboard only |
| **Scope** | Limited to specific dashboard |
| **Lifetime** | 5 menit |
| **Auto-refresh?** | Ya (by Superset SDK) |
| **Sent to frontend?** | ✅ YES |

### Membuat Guest Token

#### Prerequisite

User yang membuat guest token harus punya permission `can_grant_guest_token`. Role Admin dan Alpha biasanya sudah punya permission ini.

#### API Call

**Endpoint**: `POST /api/v1/security/guest_token/`

**Headers**: Authorization dengan service account token

**Request Body**:
```json
{
  "user": {
    "username": "guest_user_123",
    "first_name": "John",
    "last_name": "Doe"
  },
  "resources": [
    {
      "type": "dashboard",
      "id": "abc-123-def-456"  // UUID dashboard
    }
  ],
  "rls": []  // Row Level Security rules (optional)
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Python Implementation

```python
# services/superset_service.py

class SupersetService:
    # ... (previous code)

    def create_guest_token(self, dashboard_uuid, user_info=None, rls_rules=None):
        """
        Buat guest token untuk embed dashboard

        Args:
            dashboard_uuid: UUID dashboard (bukan integer ID!)
            user_info: Optional user info untuk audit
            rls_rules: Optional Row Level Security rules

        Returns:
            Guest token string
        """
        # Get service account token first
        service_token = self.get_service_token()

        headers = {
            "Authorization": f"Bearer {service_token}",
            "Content-Type": "application/json"
        }

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

        # Call API
        response = requests.post(
            f"{self.base_url}/api/v1/security/guest_token/",
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        return response.json()['token']

    def create_guest_token_with_user_context(self, dashboard_uuid, django_user):
        """
        Buat guest token dengan context Django user
        """
        user_info = {
            "username": django_user.username,
            "first_name": django_user.first_name,
            "last_name": django_user.last_name
        }

        # Optional: Add Row Level Security
        rls_rules = []
        if hasattr(django_user, 'profile'):
            department = django_user.profile.department
            rls_rules.append({
                "clause": f"department = '{department}'"
            })

        return self.create_guest_token(
            dashboard_uuid=dashboard_uuid,
            user_info=user_info,
            rls_rules=rls_rules
        )
```

### Guest Token Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    COMPLETE WORKFLOW                    │
└─────────────────────────────────────────────────────────┘

1. User browse dashboard list
   │ Django backend → Superset API (service token)
   │ GET /api/v1/dashboard/
   └─→ Return list dashboards

2. User click "View Dashboard X"
   │ Django render page dengan dashboard_uuid
   └─→ Frontend loads with dashboard UUID

3. Frontend JavaScript runs
   │ Call Django API: POST /api/guest-token/
   │ Body: { dashboard_uuid: "abc-123" }
   └─→ Django receives request

4. Django backend creates guest token
   │ Use service token to call Superset
   │ POST /api/v1/security/guest_token/
   │ With dashboard UUID
   └─→ Superset returns guest token

5. Django sends guest token to frontend
   │ Response: { guest_token: "eyJ..." }
   └─→ Frontend receives token

6. Frontend embeds dashboard
   │ Use Superset Embedded SDK
   │ Pass guest token + dashboard UUID
   └─→ Dashboard renders in iframe

7. After 5 minutes
   │ Guest token expires
   │ SDK auto-calls fetchGuestToken() again
   │ Repeat steps 3-6
   └─→ Dashboard continues working
```

### Django Implementation

#### Backend (Django Views)

```python
# views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
import json

@login_required
def dashboard_view(request, dashboard_uuid):
    """
    Page untuk view embedded dashboard
    """
    context = {
        'dashboard_uuid': dashboard_uuid,
        'superset_url': settings.SUPERSET_CONFIG['base_url']
    }
    return render(request, 'dashboard_view.html', context)


@login_required
def get_guest_token(request):
    """
    API endpoint untuk frontend request guest token
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        dashboard_uuid = data.get('dashboard_uuid')

        if not dashboard_uuid:
            return JsonResponse({
                'success': False,
                'error': 'dashboard_uuid required'
            }, status=400)

        # Create guest token
        superset = SupersetService()
        guest_token = superset.create_guest_token_with_user_context(
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
```

#### Frontend (JavaScript)

```html
<!-- templates/dashboard_view.html -->
<div id="superset-container"></div>

<script src="https://unpkg.com/@superset-ui/embedded-sdk"></script>
<script>
    const dashboardUuid = "{{ dashboard_uuid }}";
    const supersetUrl = "{{ superset_url }}";

    // Function to fetch guest token from Django
    async function fetchGuestToken() {
        const response = await fetch('/api/guest-token/', {
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
    }

    // Embed dashboard
    supersetEmbeddedSdk.embedDashboard({
        id: dashboardUuid,
        supersetDomain: supersetUrl,
        mountPoint: document.getElementById('superset-container'),
        fetchGuestToken: fetchGuestToken,  // SDK will call this
        dashboardUiConfig: {
            hideTitle: false,
            hideChartControls: false,
        }
    });

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
</script>
```

### Row Level Security (RLS)

Guest token mendukung Row Level Security untuk filter data berdasarkan user.

#### Example: Filter by Department

```python
def create_guest_token_with_rls(self, dashboard_uuid, django_user):
    """
    Create guest token dengan RLS filter
    User hanya bisa lihat data dari department mereka
    """
    # Get user department
    department = django_user.profile.department

    # RLS rules
    rls_rules = [
        {
            "clause": f"department = '{department}'"
        }
    ]

    # Create token
    return self.create_guest_token(
        dashboard_uuid=dashboard_uuid,
        user_info={
            "username": django_user.username,
            "first_name": django_user.first_name,
            "last_name": django_user.last_name
        },
        rls_rules=rls_rules
    )
```

#### Example: Multiple Filters

```python
rls_rules = [
    {
        "clause": f"department = '{user.department}'"
    },
    {
        "clause": f"region IN ({','.join(user.allowed_regions)})"
    },
    {
        "clause": f"created_date >= '{user.start_date}'"
    }
]
```

### Guest Token Limitations

❌ **Apa yang TIDAK bisa dilakukan dengan Guest Token:**

1. List dashboards (gunakan service token)
2. Create/Edit/Delete dashboards
3. Access SQL Lab
4. Change permissions
5. View dashboards selain yang dispesifikasi
6. Access Superset UI

✅ **Apa yang BISA dilakukan:**

1. View specific dashboard yang di-assign
2. Interact dengan dashboard (filters, drill-down)
3. Export chart images
4. Refresh data (jika diizinkan)

---

## Comparison Matrix

| Feature | Service Account Token | Guest Token |
|---------|----------------------|-------------|
| **Created by** | Direct login | API call (using service token) |
| **Used by** | Backend | Frontend |
| **Lifetime** | ~1 hour | 5 minutes |
| **Auto-refresh** | No (manual) | Yes (by SDK) |
| **Scope** | Full API access | Single dashboard only |
| **Permissions** | Based on role | Public role + RLS |
| **Sent to frontend** | ❌ NO | ✅ YES |
| **Cached** | ✅ YES | ❌ NO |
| **Use case** | API operations | Embedding dashboards |
| **Security risk if leaked** | ⚠️ HIGH | ✅ LOW (expires quickly) |

---

## Security Best Practices

### Service Account Token

1. **Store Securely**
```python
# ✅ Good
os.getenv('SUPERSET_SERVICE_PASSWORD')

# ❌ Bad
password = "hardcoded_password"
```

2. **Cache Appropriately**
```python
# Cache for less than token lifetime
cache.set('token', token, timeout=3000)  # 50 minutes
```

3. **Rotate Regularly**
```bash
# Change password every 90 days
# Update .env file
# Clear cache
```

4. **Monitor Usage**
```python
# Log all service account API calls
logger.info(f"Service account called: {endpoint}")
```

5. **Least Privilege**
```python
# Use Alpha role instead of Admin if possible
# Create custom role dengan minimal permissions
```

### Guest Token

1. **Validate Dashboard Access**
```python
# Check if user allowed to view dashboard
if not user_can_view_dashboard(user, dashboard_uuid):
    return JsonResponse({'error': 'Forbidden'}, status=403)
```

2. **Add User Context**
```python
# Always include actual user info, not generic "guest"
user_info = {
    "username": django_user.username,
    # ...
}
```

3. **Use RLS When Appropriate**
```python
# Filter data based on user permissions
rls_rules = get_user_rls_rules(django_user)
```

4. **Rate Limiting**
```python
# Limit guest token generation
from django.core.cache import cache

rate_limit_key = f"guest_token_rate_{user.id}"
if cache.get(rate_limit_key):
    return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

cache.set(rate_limit_key, True, timeout=10)  # 10 seconds
```

5. **Audit Logging**
```python
# Log every guest token creation
logger.info(f"Guest token created: user={user.username}, dashboard={uuid}")
```

---

## Configuration

### superset_config.py

```python
# Guest token configuration
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = os.getenv('GUEST_TOKEN_SECRET', 'your-secret-key')
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# Enable embedding
FEATURE_FLAGS = {
    'EMBEDDED_SUPERSET': True,
}

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

---

## Troubleshooting

### Service Token Issues

**Problem**: Login fails with 401
```
Solution:
- Check username/password
- Verify user is active
- Check database connectivity
```

**Problem**: Token expires too quickly
```python
# Superset config
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
```

**Problem**: Permission denied on API calls
```
Solution:
- Check user role (Admin/Alpha/Gamma)
- Verify service account has necessary permissions
- Run: superset init (to sync permissions)
```

### Guest Token Issues

**Problem**: 403 Forbidden when creating guest token
```
Solution:
- Ensure service account has can_grant_guest_token permission
- Check dashboard is Published (not Draft)
- Verify Public role has access to dashboard
```

**Problem**: Guest token doesn't work for dashboard
```
Solution:
- Dashboard must be Published
- Public role must have access (DASHBOARD_RBAC)
- Or Public role must have dataset permissions
- Check FEATURE_FLAGS: EMBEDDED_SUPERSET = True
```

**Problem**: CORS error in browser
```python
# superset_config.py
ENABLE_CORS = True
CORS_OPTIONS = {
    'origins': ['http://your-django-domain.com']
}
```

**Problem**: Guest token expires immediately
```python
# Increase lifetime if needed (default 5 min)
GUEST_TOKEN_JWT_EXP_SECONDS = 600  # 10 minutes
```

---

## Next Steps

- [Dashboard Visibility & Permissions →](./04-dashboard-permissions.md)
- [Django Integration Guide →](./05-django-integration.md)
