# Implementasi Lengkap: Django + Superset Integration

Dokumentasi implementasi lengkap integrasi Django dengan Apache Superset menggunakan Docker Compose, PostgreSQL, Caddy, Service Account Token, dan Guest Token.

## 📋 Overview Implementasi

Implementasi ini mencakup:

1. ✅ Docker Compose setup lengkap
2. ✅ PostgreSQL database dengan dummy data anggaran
3. ✅ Caddy sebagai reverse proxy
4. ✅ Service Account Token untuk backend operations
5. ✅ Guest Token untuk embedding dashboards
6. ✅ Public access tanpa login
7. ✅ Dashboard visibility control (Public/Private)

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                      Architecture                           │
└─────────────────────────────────────────────────────────────┘

Public User (No Login Required)
    ↓
Caddy Proxy (Port 80)
    ↓
Django Application (Port 8000)
    ↓
    ├─→ Service Account Token → Superset API
    │   - List dashboards
    │   - Get dashboard info
    │   - Create guest tokens
    │
    └─→ Guest Token → Frontend
        └─→ Superset Embedded SDK
            └─→ View Dashboard (iframe)

Supporting Services:
- PostgreSQL: Django DB + Superset Metadata + Budget Data
- Redis: Superset caching + Celery
```

## 📂 Struktur File

```
superset-django-2/
├── docker-compose.yml              # Orchestration (no 'version')
├── init-db.sql                     # DB init + dummy data
├── .env                            # Environment variables
├── .env.example                    # Template
├── .gitignore                      # Git ignore
├── start.sh                        # Start script
├── stop.sh                         # Stop script
├── README.md                       # Main documentation
│
├── docs/                           # Documentation
│   ├── README.md
│   ├── 01-apache-superset-overview.md
│   ├── 02-superset-api.md
│   ├── 03-authentication-tokens.md
│   ├── 04-dashboard-permissions.md
│   ├── 05-django-integration.md
│   └── 06-implementation-complete.md  # This file
│
├── caddy/
│   └── Caddyfile                   # Reverse proxy config
│
├── superset_config/
│   └── superset_config.py          # Superset configuration
│
└── django_app/
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    │
    ├── config/                     # Django project
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── dashboards/                 # Main app
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── admin.py
    │   ├── views.py                # Public views
    │   ├── urls.py
    │   └── templates/dashboards/
    │       ├── base.html
    │       ├── home.html
    │       ├── dashboard_list.html
    │       ├── dashboard_view.html
    │       └── dashboard_error.html
    │
    └── services/
        ├── __init__.py
        └── superset_service.py     # Superset API client
```

## 🗄️ Database Schema

### Tables Created

1. **opd** (Organisasi Perangkat Daerah)
   - id, kode_opd, nama_opd, kepala_opd, alamat

2. **program**
   - id, opd_id, kode_program, nama_program, tahun_mulai, tahun_selesai

3. **kegiatan** (Activities)
   - id, program_id, kode_kegiatan, nama_kegiatan

4. **kategori_belanja**
   - id, kode_kategori, nama_kategori, jenis

5. **rencana_anggaran**
   - id, kegiatan_id, kategori_belanja_id, tahun, triwulan, bulan
   - nilai_anggaran, sumber_dana

6. **realisasi_anggaran**
   - id, rencana_anggaran_id, kegiatan_id, kategori_belanja_id
   - tahun, triwulan, bulan, tanggal_realisasi
   - nilai_realisasi, persentase_realisasi

7. **v_summary_anggaran** (View)
   - Join semua tables untuk reporting

### Dummy Data Statistics

- **8 OPD**: Pendidikan, Kesehatan, PU, Sosial, Pertanian, Perhubungan, Pariwisata, BPKAD
- **12 Program**: Berbagai program per OPD
- **25 Kegiatan**: Activities under programs
- **7 Kategori Belanja**: Pegawai, Barang/Jasa, Modal, Bantuan Sosial, dll
- **82 Rencana Anggaran**: Budget plans untuk 2024
- **82 Realisasi Anggaran**: Actual spending dengan varying percentages (75%-100%)

### Example Data

```sql
-- OPD Example
INSERT INTO opd VALUES
(1, 'OPD-001', 'Dinas Pendidikan', 'Dr. Ahmad Suryanto', 'Jl. Pendidikan No. 1');

-- Program Example
INSERT INTO program VALUES
(1, 1, 'PROG-001', 'Program Peningkatan Kualitas Pendidikan Dasar',
 'Peningkatan mutu pendidikan SD dan SMP', 2024, 2026);

-- Kegiatan Example
INSERT INTO kegiatan VALUES
(1, 1, 'KEG-001', 'Pelatihan Guru SD dan SMP',
 'Pelatihan peningkatan kompetensi guru');

-- Rencana Anggaran Example (Q1 2024)
INSERT INTO rencana_anggaran VALUES
(1, 1, 2, 2024, 1, 1, 150000000, 'APBD', 'Pelatihan Batch 1');

-- Realisasi Anggaran Example (98.67% realized)
INSERT INTO realisasi_anggaran VALUES
(1, 1, 1, 2, 2024, 1, 1, '2024-01-25', 148000000, 2000000, 98.67,
 'Pelatihan selesai dengan baik');
```

## 🔧 Docker Compose Configuration

### Key Points

1. **No version field**: Removed as obsolete in newer Docker Compose
2. **Health checks**: All services have proper health checks
3. **Depends on**: Proper dependency chain
4. **Volumes**: Persistent data for PostgreSQL and Superset
5. **Networks**: Isolated bridge network

### Services

```yaml
services:
  postgres:
    - PostgreSQL 15
    - Two databases: superset, django_db
    - Init script for dummy data

  redis:
    - Redis 7
    - Caching and Celery broker

  superset:
    - Apache Superset latest
    - Auto admin creation
    - Custom config mounted

  django:
    - Python 3.11
    - Custom Dockerfile
    - Volume mount for live reload

  caddy:
    - Caddy 2
    - Reverse proxy
    - Auto HTTPS capable
```

## 🐍 Django Implementation

### SupersetService Class

Lengkap dengan:

```python
class SupersetService:
    # Authentication
    def get_service_token()          # Cached service token
    def _login()                     # Login to Superset
    def invalidate_token()           # Force refresh

    # Dashboard Operations
    def list_dashboards()            # All dashboards
    def get_dashboard()              # Dashboard detail
    def get_dashboard_visibility_info()  # Check if public
    def list_public_dashboards()     # Only public ones

    # Guest Token
    def create_guest_token()         # Generate guest token
    def can_create_guest_token_for() # Check accessibility

    # Utilities
    def format_dashboard_for_frontend()
```

### Views

#### Public Access (No Login Required)

```python
def home(request)
    # Home page

def dashboard_list_page(request)
    # List page (no login)

def dashboard_list_api(request)
    # API: Get public dashboards only

def dashboard_view(request, dashboard_uuid)
    # View embedded dashboard (no login)

@csrf_exempt
def get_guest_token(request)
    # API: Generate guest token
    # Public endpoint for Superset SDK
```

### Templates

1. **base.html**: Bootstrap 5 base template
2. **home.html**: Landing page dengan info
3. **dashboard_list.html**: Grid of public dashboards
4. **dashboard_view.html**: Embedded dashboard with SDK
5. **dashboard_error.html**: Error handling

### Key Features

- **No authentication required** for public dashboards
- **Responsive design** with Bootstrap 5
- **Real-time loading** with JavaScript fetch API
- **Error handling** with user-friendly messages
- **Superset Embedded SDK** integration

## ⚙️ Superset Configuration

### Key Settings

```python
# Feature Flags
FEATURE_FLAGS = {
    'DASHBOARD_RBAC': True,          # Role-based dashboard access
    'EMBEDDED_SUPERSET': True,       # Enable embedding
    'DASHBOARD_NATIVE_FILTERS': True,
    'GLOBAL_ASYNC_QUERIES': True,
}

# Guest Token
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_EXP_SECONDS = 300    # 5 minutes

# CORS (allow Django to embed)
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'origins': ['*'],  # Configure for production
}

# Public Role
PUBLIC_ROLE_LIKE = None              # No default public access

# Caching with Redis
CACHE_CONFIG = {...}
DATA_CACHE_CONFIG = {...}

# Celery for async
class CeleryConfig:
    broker_url = 'redis://redis:6379/0'
```

## 🌐 Caddy Configuration

Simple reverse proxy:

```
:80 {
    handle /* {
        reverse_proxy django:8000
    }

    log {
        output stdout
        format json
    }
}
```

**Production**: Just add domain name and Caddy auto-enables HTTPS.

## 🔐 Security Implementation

### Service Account Token Flow

```
1. Django backend starts
2. SupersetService.get_service_token() called
3. Login to Superset with service credentials
4. Token cached for 50 minutes
5. Token used for:
   - list_dashboards()
   - get_dashboard_visibility_info()
   - create_guest_token()
6. Token NOT sent to frontend
7. Auto-refresh on 401
```

### Guest Token Flow

```
1. User visits /dashboard/{uuid}/
2. Frontend loads Superset Embedded SDK
3. SDK calls fetchGuestToken() function
4. Frontend → POST /api/guest-token/
   Body: { dashboard_uuid: "..." }
5. Django backend:
   - Check if dashboard is public
   - Use service token to call Superset API
   - POST /api/v1/security/guest_token/
   - Return guest token to frontend
6. Frontend embeds dashboard with guest token
7. Guest token expires after 5 minutes
8. SDK auto-calls fetchGuestToken() again
9. Repeat from step 4
```

### Dashboard Visibility Control

```
Dashboard is PUBLIC if:
✅ Status = Published (not Draft)
✅ Has "Public" role assigned

Django only shows public dashboards:
- list_public_dashboards() filters by:
  - published = True
  - "Public" in roles
```

## 📝 Environment Variables

### Required Variables

```bash
# Database
POSTGRES_DB=superset
POSTGRES_USER=superset
POSTGRES_PASSWORD=<strong-password>

# Superset
SUPERSET_SECRET_KEY=<random-string>
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=<admin-password>
GUEST_TOKEN_JWT_SECRET=<token-secret>

# Service Account
SUPERSET_SERVICE_USER=django_service
SUPERSET_SERVICE_PASSWORD=<service-password>

# Django
DEBUG=True  # False in production
DJANGO_SECRET_KEY=<django-secret>
ALLOWED_HOSTS=localhost,127.0.0.1,django,caddy

# URLs
SUPERSET_URL=http://superset:8088
```

### Security Notes

- Change all default passwords
- Use strong random strings for secrets
- Keep .env out of git (.gitignore)
- Use different passwords for each service
- In production: DEBUG=False, specific ALLOWED_HOSTS

## 🚀 Deployment Steps

### Development (Local)

```bash
# 1. Clone and setup
cd superset-django-2
cp .env.example .env
# Edit .env with your passwords

# 2. Start services
./start.sh

# 3. Create service account
docker exec -it superset bash
superset fab create-user \
  --username django_service \
  --firstname Django \
  --lastname Service \
  --email service@example.com \
  --password <SUPERSET_SERVICE_PASSWORD> \
  --role Admin
exit

# 4. Setup Superset
# - Login: http://localhost:8088
# - Create database connection
# - Create datasets from v_summary_anggaran
# - Create dashboards and charts
# - Publish + assign Public role

# 5. Test
# - Open: http://localhost
# - Should see public dashboards
```

### Production

```bash
# 1. Update .env for production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SUPERSET_URL=https://superset.yourdomain.com

# 2. Update Caddyfile
yourdomain.com {
    reverse_proxy django:8000
}

superset.yourdomain.com {
    reverse_proxy superset:8088
}

# 3. Use strong passwords
# Generate with: openssl rand -base64 32

# 4. Deploy
docker compose up -d

# 5. Setup firewall
# Only expose ports 80, 443

# 6. Setup monitoring
# Logs: docker compose logs -f

# 7. Backup strategy
# - Database: pg_dump
# - Volumes: docker volume backup
```

## 🧪 Testing

### Test Service Account

```bash
docker exec -it django-app python manage.py shell

from services.superset_service import SupersetService
superset = SupersetService()

# Test login
token = superset.get_service_token()
print(f"Token: {token[:50]}...")

# Test list dashboards
dashboards = superset.list_dashboards()
print(f"Found {len(dashboards)} dashboards")

for d in dashboards:
    print(f"- {d['dashboard_title']}")
    print(f"  Published: {d.get('published')}")
    print(f"  Roles: {[r['name'] for r in d.get('roles', [])]}")
```

### Test Guest Token

```bash
# In Django shell
dashboard_uuid = "your-dashboard-uuid"

# Check if can create guest token
can_create, reason = superset.can_create_guest_token_for(dashboard_uuid)
print(f"Can create: {can_create}, Reason: {reason}")

# Create guest token
if can_create:
    token = superset.create_guest_token(dashboard_uuid)
    print(f"Guest token: {token[:50]}...")
```

### Test Public Access

```bash
# Open incognito browser
# Navigate to: http://localhost

# Should see:
# - Home page
# - "Lihat Dashboard Publik" button
# - List of public dashboards (if any published)
# - Click dashboard → embedded view
# - No login required
```

## 📊 Creating Dashboards

### Step-by-Step Guide

#### 1. Connect Database

```
Superset UI → Data → Databases → + Database
- Type: PostgreSQL
- Host: postgres
- Port: 5432
- Database: superset
- User: superset
- Password: (from .env)
→ Test Connection → Save
```

#### 2. Create Dataset

```
Data → Datasets → + Dataset
- Database: PostgreSQL
- Schema: public
- Table: v_summary_anggaran
→ Create Dataset
```

#### 3. Create Charts

**Example: Bar Chart - Anggaran per OPD**

```
Charts → + Chart
- Dataset: v_summary_anggaran
- Type: Bar Chart
- Configuration:
  - X-axis: nama_opd
  - Metric: SUM(nilai_anggaran)
  - Filters: tahun = 2024
→ Run → Save to Dashboard
```

**Example: Line Chart - Realisasi per Triwulan**

```
Charts → + Chart
- Dataset: v_summary_anggaran
- Type: Line Chart
- Configuration:
  - X-axis: triwulan
  - Metrics: SUM(nilai_realisasi), SUM(nilai_anggaran)
  - Series: nama_opd (optional)
→ Run → Save to Dashboard
```

**Example: Pie Chart - Kategori Belanja**

```
Charts → + Chart
- Dataset: v_summary_anggaran
- Type: Pie Chart
- Configuration:
  - Dimension: nama_kategori
  - Metric: SUM(nilai_anggaran)
→ Run → Save to Dashboard
```

#### 4. Create Dashboard

```
Dashboards → + Dashboard
- Name: "Dashboard Anggaran 2024"
- Add created charts
- Arrange layout
→ Save
```

#### 5. Make Public (CRITICAL!)

```
Open Dashboard → Badge: [DRAFT]
→ Click badge → Changes to [PUBLISHED]

Then:
→ ... → Edit properties → Tab: Access
→ Section: Roles → Check "Public"
→ Save
```

**Verify**:
- Badge shows: **PUBLISHED**
- Roles include: **Public**
- Now visible at http://localhost

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Service Account Login Failed

**Symptoms**:
```
ERROR: Failed to authenticate with Superset
```

**Solutions**:
```bash
# Check service account exists
docker exec -it superset superset fab list-users

# Check password matches .env
cat .env | grep SUPERSET_SERVICE_PASSWORD

# Recreate service account
docker exec -it superset bash
superset fab delete-user --username django_service
superset fab create-user ...
exit

# Restart Django
docker compose restart django
```

#### 2. Dashboard Not in Public List

**Symptoms**:
- Dashboard exists in Superset
- Not showing at http://localhost/dashboards/

**Solutions**:
```
✅ Check dashboard status = PUBLISHED (not Draft)
✅ Check Public role is assigned
✅ Restart Django: docker compose restart django
✅ Check logs: docker compose logs django
```

#### 3. Guest Token Error 403

**Symptoms**:
```
Error: Dashboard not accessible via guest token
```

**Solutions**:
```
✅ Ensure DASHBOARD_RBAC enabled in superset_config.py
✅ Ensure EMBEDDED_SUPERSET enabled
✅ Restart Superset: docker compose restart superset
✅ Check dashboard has Public role
✅ Run: docker exec -it superset superset init
```

#### 4. CORS Error in Browser

**Symptoms**:
```
Access-Control-Allow-Origin error in console
```

**Solutions**:
```python
# In superset_config.py
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'origins': ['*'],  # Or specific domain
}

# Restart Superset
docker compose restart superset
```

#### 5. Port Already in Use

**Symptoms**:
```
Error: Bind for 0.0.0.0:80 failed
```

**Solutions**:
```bash
# Check what's using port 80
sudo lsof -i :80

# Stop conflicting service
sudo systemctl stop apache2
# or
sudo systemctl stop nginx

# Or change port in docker-compose.yml
ports: - "8080:80"
```

#### 6. Database Connection Failed

**Symptoms**:
```
Could not connect to database
```

**Solutions**:
```bash
# Wait for PostgreSQL to be ready
docker compose logs postgres

# Check health
docker exec superset-postgres pg_isready

# Recreate if needed
docker compose down
docker compose up -d
```

## 📈 Performance Optimization

### Caching Strategy

```python
# Already configured in superset_config.py

# Query result cache
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
}

# Metadata cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes
}

# Thumbnail cache
THUMBNAIL_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
}
```

### Django Optimization

```python
# In settings.py

# Use Redis cache in production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/5',
    }
}

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Database Optimization

```sql
-- Indexes already created in init-db.sql

CREATE INDEX idx_rencana_tahun_triwulan ON rencana_anggaran(tahun, triwulan);
CREATE INDEX idx_realisasi_tahun_triwulan ON realisasi_anggaran(tahun, triwulan);
-- etc...
```

## 🔒 Security Checklist

### Production Deployment

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (32+ characters random)
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use specific CORS origins (not *)
- [ ] Enable HTTPS (Caddy automatic with domain)
- [ ] Use environment variables for secrets
- [ ] Regular backups of PostgreSQL
- [ ] Monitor logs for suspicious activity
- [ ] Update Docker images regularly
- [ ] Use firewall (only expose 80, 443)
- [ ] Limit Superset admin access
- [ ] Review dashboard permissions regularly

## 🎓 Learning Resources

### Implemented Concepts

1. **Docker Compose Orchestration**
   - Multi-container setup
   - Health checks
   - Dependencies
   - Volumes and networks

2. **Django Public Views**
   - No authentication required
   - CSRF exempt for public APIs
   - Service integration

3. **Superset API Integration**
   - Service account authentication
   - Guest token generation
   - Dashboard visibility control

4. **Frontend Embedding**
   - Superset Embedded SDK
   - iframe embedding
   - Token refresh handling

5. **Database Design**
   - Government budget schema
   - Views for reporting
   - Indexes for performance

## 📚 References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Apache Superset Docs](https://superset.apache.org/docs/6.0.0/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Caddy Web Server](https://caddyserver.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🔄 Maintenance

### Regular Tasks

```bash
# Update Docker images
docker compose pull
docker compose up -d

# Backup database
docker exec superset-postgres pg_dump -U superset superset > backup.sql

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Clean up
docker system prune
```

### Monitoring

```bash
# Check service status
docker compose ps

# Check resource usage
docker stats

# Check logs for errors
docker compose logs --tail=100 | grep ERROR
```

## ✅ Conclusion

Implementasi ini menyediakan:

1. ✅ **Complete Docker setup** dengan semua dependencies
2. ✅ **Dummy data lengkap** untuk government budget
3. ✅ **Public access** tanpa authentication
4. ✅ **Service + Guest token** combination
5. ✅ **Dashboard visibility control** by creators
6. ✅ **Production-ready** dengan security best practices
7. ✅ **Well-documented** dengan troubleshooting guides
8. ✅ **Easy deployment** dengan start/stop scripts

Siap digunakan untuk transparansi anggaran pemerintah daerah! 🎉

---

**Next Steps**: Deploy to production, customize templates, add more visualizations!
