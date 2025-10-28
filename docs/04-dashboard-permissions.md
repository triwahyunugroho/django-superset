# Dashboard Visibility & Permissions

## Overview

Superset menyediakan beberapa mekanisme untuk mengontrol siapa yang bisa akses dashboard. Pemahaman tentang mekanisme ini sangat penting, terutama untuk menentukan apakah dashboard bisa diakses via **Guest Token** atau tidak.

## 3 Mekanisme Permission Control

### 1. Draft vs Published Status
**Level**: Dashboard
**Control**: Owner & Admin only

### 2. Dashboard RBAC (Role-Based Access Control)
**Level**: Dashboard
**Control**: Role assignment

### 3. Dataset Permissions
**Level**: Dataset
**Control**: Implicit dashboard access

---

## 1. Draft vs Published Status

### Konsep

Setiap dashboard memiliki status: **Draft** atau **Published**.

| Status | Visibility | Guest Token Access |
|--------|-----------|-------------------|
| **Draft** | Owner & Admin only | ❌ NO |
| **Published** | Based on permissions | ✅ YES (if other conditions met) |

### Use Cases

**Draft**:
- Dashboard dalam development
- Testing dan QA
- Belum siap untuk production
- Perlu review dari team

**Published**:
- Dashboard ready untuk users
- Stable dan tested
- Documented
- Approved by stakeholders

### Mengubah Status via UI

```
1. Buka dashboard
2. Di bagian atas, ada badge "DRAFT" atau "PUBLISHED"
3. Klik badge untuk toggle status

┌─────────────────────────────────────┐
│  📊 Sales Dashboard      [DRAFT]    │  ← Klik untuk publish
└─────────────────────────────────────┘

Setelah klik:

┌─────────────────────────────────────┐
│  📊 Sales Dashboard   [PUBLISHED]   │
└─────────────────────────────────────┘
```

### Mengubah Status via API

```python
import requests

dashboard_id = 123
access_token = "your_token"

url = f"http://localhost:8088/api/v1/dashboard/{dashboard_id}"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

payload = {
    "published": True  # True = Published, False = Draft
}

response = requests.put(url, headers=headers, json=payload)
```

### Permissions

| Role | Can View Draft | Can Publish | Can Unpublish |
|------|---------------|-------------|---------------|
| **Owner** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Others** | ❌ No | ❌ No | ❌ No |

---

## 2. Dashboard RBAC

### Konsep

**Dashboard RBAC** memungkinkan assignment role-role specific ke dashboard tertentu. User dengan role yang di-assign bisa akses dashboard tersebut.

### Enable Dashboard RBAC

```python
# superset_config.py
FEATURE_FLAGS = {
    'DASHBOARD_RBAC': True,
}
```

**Note**: Setelah enable, restart Superset dan run `superset init`.

### Cara Kerja

```
Dashboard X memiliki roles: [Public, Gamma, Sales_Team]
│
├─ User dengan role "Public" → ✅ Bisa akses
├─ User dengan role "Gamma" → ✅ Bisa akses
├─ User dengan role "Sales_Team" → ✅ Bisa akses
├─ User dengan role "Finance_Team" → ❌ Tidak bisa akses
└─ Guest Token (menggunakan Public role) → ✅ Bisa akses
```

### Assign Roles ke Dashboard via UI

```
1. Buka dashboard
2. Klik menu "..." (three dots) di kanan atas
3. Pilih "Edit properties"
4. Tab "Access"
5. Section "Roles" - pilih roles yang boleh akses:

┌─────────────────────────────────────┐
│  Dashboard Roles                    │
│  ☐ Admin                            │
│  ☐ Alpha                            │
│  ☑ Gamma                            │
│  ☑ Public      ← Centang ini untuk guest token access │
│  ☐ Finance_Team                     │
│  ☑ Sales_Team                       │
└─────────────────────────────────────┘
```

### Assign Roles via API

```python
dashboard_id = 123

# Get current dashboard info first
response = requests.get(
    f"http://localhost:8088/api/v1/dashboard/{dashboard_id}",
    headers={"Authorization": f"Bearer {token}"}
)
current_data = response.json()['result']

# Update roles
url = f"http://localhost:8088/api/v1/dashboard/{dashboard_id}"
payload = {
    "roles": [
        {"id": 1, "name": "Public"},    # ← Enable guest token
        {"id": 2, "name": "Gamma"},
        {"id": 5, "name": "Sales_Team"}
    ]
}

response = requests.put(url, headers=headers, json=payload)
```

### Public Role

**Public** role adalah role khusus yang digunakan oleh:
- Guest tokens
- Anonymous users (jika PUBLIC_ROLE_LIKE configured)

**Untuk enable guest token access ke dashboard:**
```
Dashboard MUST have "Public" role assigned
```

### Jika Tidak Ada Roles

Jika dashboard tidak memiliki role yang di-assign (kosong):
- Fallback ke dataset permissions (explained below)
- Semua user dengan akses ke datasets bisa akses dashboard

---

## 3. Dataset Permissions

### Konsep

Jika **Dashboard RBAC tidak enabled** atau dashboard tidak punya roles, akses ditentukan oleh **dataset permissions**.

```
Dashboard menggunakan Dataset A, B, C
│
├─ User punya akses ke A, B, C → ✅ Bisa akses dashboard
├─ User punya akses ke A, B only → ❌ Tidak bisa akses dashboard
└─ User punya akses ke A only → ❌ Tidak bisa akses dashboard
```

User harus punya akses ke **SEMUA datasets** yang digunakan dashboard.

### Cara Kerja

1. Dashboard berisi charts
2. Setiap chart menggunakan dataset
3. User harus punya permission ke semua datasets
4. Permission format: `datasource access on [dataset_name]`

### Grant Dataset Permission via UI

```
1. Settings > List Roles
2. Pilih role (contoh: "Public")
3. Tab "Permissions"
4. Search "datasource access"
5. Centang datasets yang ingin diakses role tersebut

┌──────────────────────────────────────────────┐
│  Public Role Permissions                     │
│                                              │
│  Search: datasource access                   │
│                                              │
│  ☑ datasource access on [sales_data]        │
│  ☑ datasource access on [products]          │
│  ☑ datasource access on [customers]         │
│  ☐ datasource access on [employee_salaries] │ ← Private
│  ☐ datasource access on [financial_records] │ ← Private
└──────────────────────────────────────────────┘
```

### Python Helper untuk Check Permissions

```python
def get_dashboard_datasets(dashboard_id):
    """Get all datasets used by dashboard"""
    superset = SupersetService()
    token = superset.get_service_token()

    # Get dashboard detail
    response = requests.get(
        f"{superset.base_url}/api/v1/dashboard/{dashboard_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    dashboard = response.json()['result']

    # Extract datasets from charts
    datasets = set()
    for chart in dashboard.get('charts', []):
        datasource_id = chart.get('datasource_id')
        if datasource_id:
            datasets.add(datasource_id)

    return list(datasets)


def check_public_role_has_access(datasets):
    """Check if Public role has access to all datasets"""
    superset = SupersetService()
    token = superset.get_service_token()

    # Get Public role permissions
    response = requests.get(
        f"{superset.base_url}/api/v1/security/roles/?q=(filters:!((col:name,opr:eq,value:Public)))",
        headers={"Authorization": f"Bearer {token}"}
    )

    public_role = response.json()['result'][0]
    permissions = public_role.get('permissions', [])

    # Check each dataset
    for dataset_id in datasets:
        has_access = any(
            f"datasource access on [{dataset_id}]" in perm['permission_name']
            for perm in permissions
        )
        if not has_access:
            return False, f"Public role missing access to dataset {dataset_id}"

    return True, "Public role has access to all datasets"
```

---

## Decision Matrix: Guest Token Access

Apakah dashboard bisa diakses via guest token?

| Condition | Result |
|-----------|--------|
| Status = Draft | ❌ **NO** (regardless of other settings) |
| Status = Published + RBAC ON + Public role assigned | ✅ **YES** |
| Status = Published + RBAC ON + Public role NOT assigned | ❌ **NO** |
| Status = Published + RBAC OFF + Public has dataset access | ✅ **YES** |
| Status = Published + RBAC OFF + Public missing dataset access | ❌ **NO** |

### Flowchart

```
Is dashboard Published?
│
├─ NO → ❌ Cannot use guest token
│
└─ YES → Is DASHBOARD_RBAC enabled?
          │
          ├─ YES → Does dashboard have Public role?
          │         │
          │         ├─ YES → ✅ Can use guest token
          │         └─ NO → ❌ Cannot use guest token
          │
          └─ NO → Does Public role have access to ALL datasets?
                    │
                    ├─ YES → ✅ Can use guest token
                    └─ NO → ❌ Cannot use guest token
```

---

## Workflow untuk Pembuat Dashboard

### Scenario 1: Public Dashboard (Guest Token Enabled)

**Goal**: Dashboard bisa diakses via guest token

```
✅ Checklist:

1. Set dashboard = Published
   - Via UI: Click DRAFT badge
   - Via API: PUT /api/v1/dashboard/{id} {"published": true}

2. Enable DASHBOARD_RBAC (recommended)
   - superset_config.py: FEATURE_FLAGS = {'DASHBOARD_RBAC': True}
   - Restart Superset

3. Assign Public role to dashboard
   - Via UI: Edit properties > Access > Roles > ☑ Public
   - Via API: PUT /api/v1/dashboard/{id} {"roles": [..., {"name": "Public"}]}

4. Test guest token
   - Create guest token via API
   - Embed dashboard
   - Verify it works

Alternative (if DASHBOARD_RBAC not enabled):
   - Grant Public role access to all datasets used by dashboard
   - Settings > List Roles > Public > Permissions
   - Check all "datasource access on [dataset]"
```

### Scenario 2: Internal Dashboard (Login Required)

**Goal**: Dashboard hanya bisa diakses dengan login regular

```
✅ Checklist:

1. Set dashboard = Published (or Draft jika masih development)

2. Assign internal roles only
   - Via UI: Edit properties > Access > Roles
   - Select: Gamma, Alpha, Finance_Team, etc.
   - DO NOT select Public

3. Test
   - Try creating guest token → Should work (token created)
   - Try accessing dashboard with guest token → Should fail 403
   - Login as Gamma user → Should work
```

### Scenario 3: Private Dashboard (Owner Only)

**Goal**: Hanya owner dan admin yang bisa akses

```
✅ Checklist:

1. Set dashboard = Draft
   - Via UI: Click PUBLISHED badge to make it Draft
   - Via API: PUT /api/v1/dashboard/{id} {"published": false}

2. No role assignment needed
   - Only owner and admin can see it

3. Add owners if needed
   - Via UI: Edit properties > Owners
   - Add specific users who should have access
```

---

## Django Integration

### Check Dashboard Accessibility

```python
# services/superset_service.py

class SupersetService:
    # ... (previous code)

    def get_dashboard_visibility_info(self, dashboard_id):
        """
        Get comprehensive visibility info for dashboard
        """
        token = self.get_service_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Get dashboard detail
        response = requests.get(
            f"{self.base_url}/api/v1/dashboard/{dashboard_id}",
            headers=headers
        )
        response.raise_for_status()

        dashboard = response.json()['result']

        # Analyze visibility
        is_published = dashboard.get('published', False)
        roles = dashboard.get('roles', [])
        role_names = [r['name'] for r in roles]
        has_public_role = 'Public' in role_names or 'public' in role_names

        # Determine if guest token will work
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
            'dashboard_id': dashboard['id'],
            'uuid': dashboard['uuid'],
            'title': dashboard['dashboard_title'],
            'published': is_published,
            'roles': role_names,
            'has_public_role': has_public_role,
            'guest_token_accessible': guest_token_accessible,
            'reason': reason,
            'owners': [o['username'] for o in dashboard.get('owners', [])]
        }

    def can_create_guest_token_for(self, dashboard_uuid):
        """
        Check if can create guest token for dashboard
        Returns: (can_create: bool, reason: str)
        """
        # Get dashboard by UUID
        token = self.get_service_token()
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{self.base_url}/api/v1/dashboard/{dashboard_uuid}",
            headers=headers
        )

        if response.status_code == 404:
            return False, "Dashboard not found"

        dashboard = response.json()['result']

        # Check published status
        if not dashboard.get('published'):
            return False, "Dashboard is in Draft mode"

        # Check roles
        roles = dashboard.get('roles', [])
        role_names = [r['name'].lower() for r in roles]

        if 'public' in role_names:
            return True, "Dashboard is accessible via guest token"

        if not roles:
            return None, "Unknown (depends on dataset permissions)"

        return False, "Dashboard does not have Public role access"
```

### Django Admin Interface

```python
# admin.py
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render

@admin.register(SupersetDashboard)
class SupersetDashboardAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_public', 'can_use_guest_token']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:dashboard_id>/visibility/',
                 self.admin_site.admin_view(self.dashboard_visibility),
                 name='dashboard-visibility'),
            path('<int:dashboard_id>/make-public/',
                 self.admin_site.admin_view(self.make_public),
                 name='dashboard-make-public'),
        ]
        return custom_urls + urls

    def dashboard_visibility(self, request, dashboard_id):
        """Show dashboard visibility info"""
        superset = SupersetService()
        info = superset.get_dashboard_visibility_info(dashboard_id)

        return JsonResponse(info)

    def make_public(self, request, dashboard_id):
        """Make dashboard public (publish + add Public role)"""
        superset = SupersetService()

        # Set published = True
        # Add Public role
        success = superset.set_dashboard_public(dashboard_id)

        if success:
            return JsonResponse({
                'success': True,
                'message': 'Dashboard is now public'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to update dashboard'
            }, status=500)
```

### Frontend Badge Display

```html
<!-- templates/dashboard_list.html -->
<div class="dashboard-card">
    <h3>{{ dashboard.title }}</h3>

    <!-- Status badges -->
    <div class="badges">
        {% if dashboard.published %}
            <span class="badge badge-success">Published</span>
        {% else %}
            <span class="badge badge-warning">Draft</span>
        {% endif %}

        {% if dashboard.guest_token_accessible %}
            <span class="badge badge-info">Public (Guest Token)</span>
        {% elif dashboard.guest_token_accessible is None %}
            <span class="badge badge-secondary">Unknown Access</span>
        {% else %}
            <span class="badge badge-secondary">Internal Only</span>
        {% endif %}
    </div>

    <!-- Roles -->
    <div class="roles">
        <small>Roles: {{ dashboard.roles|join:", " }}</small>
    </div>

    <!-- Actions -->
    {% if dashboard.guest_token_accessible %}
        <button onclick="embedDashboard('{{ dashboard.uuid }}')">
            View Embedded Dashboard
        </button>
    {% else %}
        <a href="{{ superset_url }}/superset/dashboard/{{ dashboard.uuid }}">
            View in Superset (Login Required)
        </a>
    {% endif %}
</div>
```

---

## Configuration Best Practices

### superset_config.py

```python
# Enable Dashboard RBAC (recommended)
FEATURE_FLAGS = {
    'DASHBOARD_RBAC': True,
    'EMBEDDED_SUPERSET': True,
}

# Guest token configuration
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = os.getenv('GUEST_TOKEN_SECRET')
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# Public role configuration
# Set to None to prevent anonymous access by default
PUBLIC_ROLE_LIKE = None

# If you want public users to have Gamma permissions:
# PUBLIC_ROLE_LIKE = "Gamma"
```

### Custom Roles

Create custom roles untuk different access levels:

```
Sales_Viewer:
- View-only access to sales dashboards
- No edit permissions
- No SQL Lab access

Finance_Analyst:
- Access to finance dashboards and datasets
- SQL Lab access to finance database
- Can create own dashboards

Executive:
- View-only access to executive dashboards
- No raw data access
- High-level KPIs only
```

---

## Troubleshooting

### Guest Token Returns 403

**Possible causes**:

1. Dashboard is Draft
```
Solution: Publish dashboard
```

2. Public role not assigned (with DASHBOARD_RBAC)
```
Solution: Add Public role to dashboard
```

3. Public role missing dataset permissions (without DASHBOARD_RBAC)
```
Solution: Grant Public role access to all datasets
```

4. EMBEDDED_SUPERSET not enabled
```python
# superset_config.py
FEATURE_FLAGS = {'EMBEDDED_SUPERSET': True}
```

### Dashboard Not Visible to User

**Possible causes**:

1. Dashboard is Draft and user is not owner/admin
```
Solution: Publish dashboard or add user as owner
```

2. User role not assigned to dashboard (with DASHBOARD_RBAC)
```
Solution: Add user's role to dashboard
```

3. User missing dataset permissions (without DASHBOARD_RBAC)
```
Solution: Grant user's role access to datasets
```

### Permissions Not Taking Effect

```bash
# Sync permissions
superset init

# Or restart Superset after config changes
```

---

## Next Steps

- [Django Integration Guide →](./05-django-integration.md)
