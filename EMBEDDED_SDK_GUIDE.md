# Superset Embedded SDK Integration Guide

## Overview

Project ini mengintegrasikan Apache Superset dengan Django menggunakan **@superset-ui/embedded-sdk**, sebuah library JavaScript yang memungkinkan embedding dashboard Superset dengan metode autentikasi yang aman menggunakan **Guest Token**.

## Keuntungan Embedded SDK vs Iframe Biasa

### Menggunakan Embedded SDK (@superset-ui/embedded-sdk)
✅ **Lebih Aman**: Menggunakan guest token untuk autentikasi
✅ **Row-Level Security**: Mendukung RLS untuk filter data per user
✅ **Kontrol UI**: Bisa hide/show title, tabs, filters, dll
✅ **Event Handling**: Bisa listen to events dari dashboard
✅ **Session Management**: Token expire otomatis untuk keamanan
✅ **Best Practice**: Recommended oleh Apache Superset

### Iframe Biasa (Metode Lama)
❌ Kurang aman (perlu set dashboard public)
❌ Tidak ada RLS
❌ Kontrol UI terbatas
❌ Tidak ada event handling
❌ X-Frame-Options issues

## Arsitektur

```
┌─────────────┐
│   Browser   │
│  (Django)   │
└──────┬──────┘
       │
       │ 1. Request Dashboard
       ▼
┌─────────────┐
│   Django    │
│   Backend   │
└──────┬──────┘
       │
       │ 2. Request Guest Token
       ▼
┌─────────────┐
│  Superset   │
│     API     │
└──────┬──────┘
       │
       │ 3. Return Guest Token
       ▼
┌─────────────┐
│   Django    │
│  Frontend   │
└──────┬──────┘
       │
       │ 4. Embed Dashboard with Token
       ▼
┌─────────────┐
│  Superset   │
│  Dashboard  │
└─────────────┘
```

## Implementasi

### 1. Backend - Guest Token Endpoint

**File**: `django/budget/views_superset.py`

Django sudah memiliki endpoint untuk generate guest token:

```python
@require_safe
def fetch_superset_guest_token(request, dashboard_id: str):
    """
    Get a guest token for integration of a Superset dashboard
    """
    # Login to Superset
    # Get CSRF token
    # Request guest token dengan:
    #   - Dashboard ID
    #   - RLS rules (optional)
    #   - User info
    # Return guest token
```

**URL**: `/superset_integration/guest_token/<dashboard_id>`

### 2. Frontend - Embedded SDK Implementation

**File**: `django/templates/budget/dashboard.html`

#### Load SDK dari CDN
```html
<script src="https://unpkg.com/@superset-ui/embedded-sdk@0.1.0-alpha.10/bundle/index.js"></script>
```

#### Fetch Guest Token
```javascript
async function fetchGuestToken() {
    const response = await fetch('/superset_integration/guest_token/{{ dashboard_id }}');
    const guestToken = await response.text();
    return guestToken;
}
```

#### Embed Dashboard
```javascript
superset.embedDashboard({
    id: "{{ superset_dashboard_id }}",              // Dashboard ID di Superset
    supersetDomain: "http://{{ superset_domain }}", // Domain Superset
    mountPoint: document.getElementById("superset-embedded-container"),
    fetchGuestToken: fetchGuestToken,               // Callback function
    dashboardUiConfig: {
        hideTitle: false,
        hideTab: false,
        hideChartControls: false,
        filters: {
            expanded: true,
            visible: true
        }
    },
    debug: true
});
```

### 3. View Context

**File**: `django/budget/views.py`

```python
def dashboard(request):
    context = {
        'dashboard_id': 1,                      # ID untuk guest token endpoint
        'superset_dashboard_id': '1',          # ID dashboard di Superset
        'superset_domain': 'localhost:8088',   # Domain Superset
    }
    return render(request, 'budget/dashboard.html', context)
```

## Configuration

### Superset Config (`superset/superset_config.py`)

```python
# Enable embedding
FEATURE_FLAGS = {
    'EMBEDDED_SUPERSET': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
}

# Guest token configuration
GUEST_ROLE_NAME = 'Gamma'
GUEST_TOKEN_JWT_SECRET = os.environ.get('SUPERSET_SECRET_KEY')
GUEST_TOKEN_JWT_ALGO = 'HS256'
GUEST_TOKEN_HEADER_NAME = 'X-GuestToken'
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# CORS for iframe embedding
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']
}

# Disable X-Frame-Options
TALISMAN_ENABLED = False
OVERRIDE_HTTP_HEADERS = {'X-Frame-Options': None}

# Session cookies
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
```

### Django Settings (`django/config/settings.py`)

```python
INSTALLED_APPS = [
    # ...
    'django_superset_integration',
    'budget',
]

# Fernet encryption key untuk menyimpan password Superset
ENCRYPTION_KEY = os.environ.get('FERNET_KEY', 'your_key').encode()
```

## Setup Instructions

### 1. Setup Django Admin

1. Login ke Django Admin: http://localhost:8000/admin/
2. Buat **SupersetInstance**:
   - Name: Superset Server
   - Address: superset:8088
   - Username: admin
   - Password: admin

3. Buat **SupersetDashboard**:
   - Dashboard Integration ID: 1 (ID dashboard dari Superset)
   - Domain: Pilih Superset Server
   - Title: Dashboard Title

### 2. Create Dashboard di Superset

1. Login ke Superset: http://localhost:8088 (admin/admin)
2. Connect database PostgreSQL:
   - Host: postgres
   - Port: 5432
   - Database: superset_db
   - User: superset_user
   - Password: superset_password

3. Buat Dataset dari tabel `budget_anggarandaerah`

4. Buat Dashboard dengan charts dari dataset tersebut

5. Catat Dashboard ID dari URL (contoh: `/superset/dashboard/1/`)

### 3. Test Embedded Dashboard

1. Buka: http://localhost:8000/dashboard/
2. Dashboard akan otomatis load menggunakan Embedded SDK
3. Check browser console untuk debug info

## Dashboard UI Configuration Options

```javascript
dashboardUiConfig: {
    // Hide/show dashboard title
    hideTitle: false,

    // Hide/show dashboard tabs
    hideTab: false,

    // Hide/show chart controls (3-dot menu)
    hideChartControls: false,

    // Filter panel configuration
    filters: {
        expanded: true,   // Auto-expand filters
        visible: true     // Show/hide filter panel
    },

    // Additional URL parameters
    urlParams: {
        standalone: 'true'
    }
}
```

## Row-Level Security (RLS)

Untuk membatasi data yang bisa diakses user, edit function `create_rls_clause` di `views_superset.py`:

```python
def create_rls_clause(user):
    """
    SQL clause to apply to the dashboard data
    """
    if not user.is_authenticated:
        return [{"clause": "1=0"}]  # No data

    # Contoh: User hanya bisa lihat data provinsi mereka
    if hasattr(user, 'provinsi_id'):
        return [{"clause": f"provinsi_id = {user.provinsi_id}"}]

    return [{"clause": "1=1"}]  # All data
```

## Troubleshooting

### Dashboard tidak muncul

1. **Check Console**: Buka browser console untuk error messages
2. **Check Guest Token**: Pastikan endpoint `/superset_integration/guest_token/1` return token
3. **Check CORS**: Pastikan CORS enabled di Superset config
4. **Check Dashboard ID**: Pastikan ID sesuai di Superset dan Django

### Guest Token Error

```
Error: Guest token fetch failed: 500
```

**Solution**:
- Pastikan SupersetInstance sudah dibuat di Django Admin
- Pastikan username/password benar
- Check Superset logs: `docker compose logs superset`

### X-Frame-Options Error

```
Refused to display in a frame because it set 'X-Frame-Options'
```

**Solution**:
- Set `TALISMAN_ENABLED = False` di `superset_config.py`
- Restart Superset: `docker compose restart superset`

### CORS Error

```
Access to fetch at 'http://localhost:8088' from origin 'http://localhost:8000' has been blocked by CORS
```

**Solution**:
- Set `ENABLE_CORS = True` di `superset_config.py`
- Add `'*'` to `CORS_OPTIONS['origins']`
- Restart Superset: `docker compose restart superset`

## Security Considerations

1. **Guest Token Expiration**: Token expire setelah 5 menit (configurable)
2. **HTTPS in Production**: Set `SESSION_COOKIE_SECURE = True` jika menggunakan HTTPS
3. **CORS Origins**: Ganti `'*'` dengan domain spesifik di production
4. **RLS**: Implementasikan RLS untuk membatasi akses data per user
5. **Fernet Key**: Ganti dengan key yang aman di production

## References

- [@superset-ui/embedded-sdk Documentation](https://www.npmjs.com/package/@superset-ui/embedded-sdk)
- [Apache Superset Embedding Documentation](https://superset.apache.org/docs/installation/embedding-superset)
- [django-superset-integration](https://pypi.org/project/django-superset-integration/)

## Next Steps

1. Implement RLS untuk multi-tenancy
2. Add error handling dan retry logic
3. Implement dashboard refresh functionality
4. Add loading states yang lebih informatif
5. Cache guest tokens (dengan memperhatikan expiration)
