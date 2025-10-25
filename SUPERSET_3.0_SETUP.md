# Superset 3.0+ Embedded SDK Setup Guide

## Problem yang Diselesaikan

Pada **Superset 3.0+**, endpoint `/api/v1/security/login` tidak tersedia lagi karena Superset sekarang menggunakan SPA (Single Page Application). Hal ini membuat package `django-superset-integration` tidak berfungsi dengan baik karena bergantung pada endpoint lama.

## Solusi: Direct JWT Guest Token Generation

Alih-alih login ke Superset API terlebih dahulu, kita generate **guest token langsung** menggunakan JWT dengan secret key yang sama seperti yang digunakan Superset.

### Cara Kerja

```
┌─────────────┐
│   Browser   │
│             │
└──────┬──────┘
       │ 1. Request Dashboard
       ▼
┌─────────────┐
│   Django    │
│  Frontend   │
└──────┬──────┘
       │ 2. fetchGuestToken()
       ▼
┌─────────────┐
│   Django    │
│   Backend   │  <-- Generate JWT token directly
│             │      using SUPERSET_SECRET_KEY
└──────┬──────┘
       │ 3. Return Guest Token (JWT)
       ▼
┌─────────────┐
│   Browser   │
│   SDK       │
└──────┬──────┘
       │ 4. Embed Dashboard with Token
       ▼
┌─────────────┐
│  Superset   │
│  Dashboard  │  <-- Validates token using same secret
└─────────────┘
```

## Implementasi

### 1. File: `django/budget/views_guest_token.py`

Generate guest token langsung tanpa perlu call Superset API:

```python
import time
import jwt
from django.http import HttpResponse, JsonResponse

@require_safe
def generate_guest_token_direct(request, dashboard_id: str):
    # Get secret key (must match Superset config)
    superset_secret = settings.SUPERSET_SECRET_KEY

    # JWT payload
    payload = {
        "user": {
            "username": "guest_user",
            "first_name": "Guest",
            "last_name": "User"
        },
        "resources": [{
            "type": "dashboard",
            "id": dashboard_id
        }],
        "rls": [],  # Row Level Security rules
        "iat": int(time.time()),
        "exp": int(time.time()) + 300,  # 5 minutes
        "type": "guest"
    }

    # Generate JWT
    token = jwt.encode(payload, superset_secret, algorithm='HS256')
    return HttpResponse(token)
```

### 2. File: `django/config/settings.py`

Tambahkan SUPERSET_SECRET_KEY:

```python
# Must match GUEST_TOKEN_JWT_SECRET in superset_config.py
SUPERSET_SECRET_KEY = os.environ.get(
    'SUPERSET_SECRET_KEY',
    'your_secret_key_change_this_in_production'
)
```

### 3. File: `django/requirements.txt`

Tambahkan PyJWT:

```
pyjwt==2.10.1
```

### 4. File: `django/budget/urls.py`

Tambahkan route untuk guest token endpoint:

```python
from .views_guest_token import generate_guest_token_direct

urlpatterns = [
    path('guest-token/<str:dashboard_id>/', generate_guest_token_direct, name='guest-token-direct'),
]
```

### 5. File: `django/templates/budget/dashboard.html`

Update `fetchGuestToken()` untuk menggunakan endpoint baru:

```javascript
async function fetchGuestToken() {
    const response = await fetch('/guest-token/{{ superset_dashboard_id }}/');
    const guestToken = await response.text();
    return guestToken;
}
```

## Konfigurasi Superset

Pastikan `superset_config.py` memiliki konfigurasi berikut:

```python
# Guest token configuration
GUEST_ROLE_NAME = 'Gamma'
GUEST_TOKEN_JWT_SECRET = os.environ.get('SUPERSET_SECRET_KEY', 'your_secret_key_change_this_in_production')
GUEST_TOKEN_JWT_ALGO = 'HS256'
GUEST_TOKEN_HEADER_NAME = 'X-GuestToken'
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# Enable embedding
FEATURE_FLAGS = {
    'EMBEDDED_SUPERSET': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_RBAC': False,
}

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
```

## Instalasi

```bash
# 1. Install PyJWT
docker compose exec django pip install pyjwt==2.10.1

# 2. Restart Django
docker compose restart django

# 3. Test guest token generation
curl http://localhost:8000/guest-token/1/
```

## Testing

### 1. Test Guest Token Endpoint

```bash
curl http://localhost:8000/guest-token/1/
```

Expected output (JWT token):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7InVzZXJuYW1lIjoiZ...
```

### 2. Decode Token (untuk debugging)

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

Output:
```python
{
    'user': {
        'username': 'guest_user',
        'first_name': 'Guest',
        'last_name': 'User'
    },
    'resources': [{'type': 'dashboard', 'id': '1'}],
    'rls': [],
    'iat': 1761359664,
    'exp': 1761359964,
    'type': 'guest'
}
```

### 3. Test Embedded Dashboard

1. Buka: http://localhost:8000/dashboard/
2. Open Browser DevTools Console
3. Lihat log:
   - `Guest token fetched successfully`
   - `Dashboard embedded successfully!`

## Keuntungan Approach Ini

### ✅ Tidak Perlu Superset API Login
- Tidak bergantung pada endpoint `/api/v1/security/login` yang deprecated
- Tidak perlu manage session ke Superset
- Lebih cepat karena skip API call

### ✅ Kompatibel dengan Superset 3.0+
- Menggunakan guest token yang native supported
- Tidak bergantung pada package `django-superset-integration` yang outdated

### ✅ Lebih Aman
- Token expire otomatis (5 menit)
- Secret key shared antara Django dan Superset
- Tidak perlu store credentials

### ✅ Mudah Customize
- Bisa tambahkan RLS rules per user
- Bisa customize user info di token
- Kontrol penuh atas token payload

## Row-Level Security (RLS)

Untuk membatasi data per user, edit payload `rls`:

```python
def generate_guest_token_direct(request, dashboard_id: str):
    # Example: Filter by user's province
    rls_rules = []

    if request.user.is_authenticated:
        if hasattr(request.user, 'provinsi_id'):
            rls_rules.append({
                "clause": f"provinsi_id = {request.user.provinsi_id}"
            })

    payload = {
        "user": {
            "username": request.user.username if request.user.is_authenticated else "guest",
            "first_name": request.user.first_name if request.user.is_authenticated else "Guest",
            "last_name": request.user.last_name if request.user.is_authenticated else "User"
        },
        "resources": [{"type": "dashboard", "id": dashboard_id}],
        "rls": rls_rules,  # Apply RLS
        "iat": int(time.time()),
        "exp": int(time.time()) + 300,
        "type": "guest"
    }

    token = jwt.encode(payload, settings.SUPERSET_SECRET_KEY, algorithm='HS256')
    return HttpResponse(token)
```

## Troubleshooting

### Token Invalid / Signature Verification Failed

**Problem**: Superset menolak token dengan error signature verification.

**Solution**:
- Pastikan `SUPERSET_SECRET_KEY` di Django **sama persis** dengan `GUEST_TOKEN_JWT_SECRET` di Superset
- Check environment variable: `docker compose exec django env | grep SUPERSET_SECRET_KEY`
- Check Superset config: `docker compose exec superset python -c "from superset import app; print(app.config['GUEST_TOKEN_JWT_SECRET'])"`

### Dashboard Tidak Muncul

**Problem**: Loading spinner terus muncul, dashboard tidak muncul.

**Solution**:
- Check browser console untuk error
- Pastikan dashboard ID benar: http://localhost:8088/superset/dashboard/1/
- Check CORS enabled di `superset_config.py`
- Check `TALISMAN_ENABLED = False`

### Token Expired

**Problem**: Dashboard error "Token expired".

**Solution**:
- Token memang expire setelah 5 menit
- Embedded SDK akan otomatis request token baru
- Jika masih error, check system time: `date`

## Environment Variables

Untuk production, gunakan environment variable:

```yaml
# docker-compose.yml
services:
  django:
    environment:
      - SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}

  superset:
    environment:
      - SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}
```

```.env
# .env file
SUPERSET_SECRET_KEY=your-very-secure-secret-key-here
```

## Kesimpulan

Dengan approach ini, kita tidak perlu bergantung pada:
1. ❌ Package `django-superset-integration` yang outdated
2. ❌ Superset API `/api/v1/security/login` yang deprecated di v3.0+
3. ❌ Database models `SupersetInstance` dan `SupersetDashboard`

Yang kita butuhkan hanya:
1. ✅ Secret key yang sama di Django dan Superset
2. ✅ PyJWT untuk generate token
3. ✅ Dashboard ID dari Superset
4. ✅ @superset-ui/embedded-sdk di frontend

Dashboard sekarang bisa di-embed dengan aman dan efisien! 🎉
