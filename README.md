# Django + Apache Superset Integration

Integrasi sederhana Django dengan Apache Superset untuk menampilkan dashboard anggaran pemerintah daerah yang dapat diakses publik tanpa login.

## 🎯 Fitur

- ✅ **Public Access**: Dashboard dapat diakses tanpa login
- ✅ **Auto Setup**: Admin user dan service account dibuat otomatis
- ✅ **Service Account Token**: Backend Django menggunakan service account untuk API calls
- ✅ **Guest Token**: Frontend menggunakan guest token untuk embed dashboard
- ✅ **Dashboard Filters**: Native filters, cross-filters, dan parameter parsing
- ✅ **Row Level Security (RLS)**: Filter data per-user menggunakan guest token
- ✅ **Dashboard Management**: Pembuat dashboard dapat menentukan visibility (public/private)
- ✅ **Docker Compose**: Setup lengkap dengan satu command
- ✅ **PostgreSQL**: Database untuk Django dan Superset
- ✅ **Redis**: Caching untuk performa optimal
- ✅ **Caddy**: Web server modern dengan auto-HTTPS
- ✅ **Dummy Data**: Data anggaran pemerintah daerah siap pakai

## 📋 Prerequisites

- Docker & Docker Compose
- Git
- 8GB RAM minimum
- Port 80, 5432, 6379, 8000, 8088 available

## 🚀 Quick Start

> **⚡ Fastest Way**: Gunakan `bash start.sh` untuk automatic setup!
>
> **📚 Complete Guide**: Lihat [docs/06-implementation-complete.md](docs/06-implementation-complete.md) untuk dokumentasi lengkap!

### 1. Clone Repository

```bash
git clone <repository-url>
cd superset-django-2
```

### 2. Copy Environment Variables (Optional)

```bash
cp .env.example .env
```

Edit `.env` file untuk mengubah password/secret keys (opsional untuk development):

```bash
# .env
POSTGRES_PASSWORD=your_secure_password
SUPERSET_SECRET_KEY=your_superset_secret
DJANGO_SECRET_KEY=your_django_secret
SUPERSET_SERVICE_PASSWORD=your_service_password
GUEST_TOKEN_JWT_SECRET=your_guest_token_secret

# Admin user credentials (auto-created on startup)
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=admin
```

### 3. Start All Services (Automatic Setup)

```bash
bash start.sh
```

Script ini akan:
- ✅ Membuat .env file dari .env.example (jika belum ada)
- ✅ Start semua Docker containers
- ✅ Menunggu semua services ready
- ✅ **Auto-create admin user** di Superset
- ✅ **Auto-create service account** untuk Django
- ✅ Menampilkan access points dan credentials

**Atau manual:**

```bash
docker compose up -d
```

Monitor progress:

```bash
docker compose logs -f superset
```

### 4. Access Applications

- **Django (Public)**: http://localhost
- **Superset (Admin)**: http://localhost:8088
  - Username: `admin`
  - Password: `admin` (atau sesuai `SUPERSET_ADMIN_PASSWORD`)

**Service Account** (untuk Django backend):
- Username: `django_service`
- Password: sesuai `SUPERSET_SERVICE_PASSWORD` di `.env`
- Role: Admin
- **Otomatis dibuat saat startup!**

## 📊 Setup Dashboard Superset

### 1. Login to Superset

Buka http://localhost:8088 dan login sebagai admin.

### 2. Connect to Database

1. Menu: **Data > Databases**
2. Click **+ Database**
3. Pilih **PostgreSQL**
4. Isi configuration:
   ```
   Host: postgres
   Port: 5432
   Database: superset
   Username: superset
   Password: superset_password_change_this
   ```
5. Test Connection
6. Save

### 3. Create Dataset

1. Menu: **Data > Datasets**
2. Click **+ Dataset**
3. Pilih:
   - **Database**: PostgreSQL
   - **Schema**: public
   - **Table**: v_summary_anggaran (view yang sudah dibuat)
4. Save

### 4. Create Dashboard

1. Menu: **Dashboards**
2. Click **+ Dashboard**
3. Beri nama, misalnya: "Dashboard Anggaran 2024"
4. Drag & drop charts atau create new charts
5. Save

### 5. Make Dashboard Public

**PENTING**: Untuk dashboard bisa diakses publik tanpa login:

1. Buka dashboard yang sudah dibuat
2. Click **...** (three dots) > **Edit properties**
3. Tab **Access**:
   - Centang **Published** (atau klik badge DRAFT untuk publish)
   - Di section **Roles**, centang **Public**
4. Save

**Verifikasi**:
- Badge di dashboard harus **PUBLISHED**
- Role "Public" harus tercantum

## 🎨 Creating Charts

### Example: Bar Chart - Anggaran per OPD

1. Create new chart
2. Dataset: `v_summary_anggaran`
3. Chart type: Bar Chart
4. Configuration:
   - **Dimensions**: `nama_opd`
   - **Metrics**: `SUM(nilai_anggaran)`
   - **Filters**: `tahun = 2024`
5. Run Query
6. Save to Dashboard

### Example: Line Chart - Realisasi per Triwulan

1. Create new chart
2. Dataset: `v_summary_anggaran`
3. Chart type: Line Chart
4. Configuration:
   - **X-axis**: `triwulan`
   - **Metrics**: `SUM(nilai_realisasi)`
   - **Breakdown**: `nama_opd`
5. Run Query
6. Save to Dashboard

### Example: Pie Chart - Kategori Belanja

1. Create new chart
2. Dataset: `v_summary_anggaran`
3. Chart type: Pie Chart
4. Configuration:
   - **Dimensions**: `nama_kategori`
   - **Metric**: `SUM(nilai_anggaran)`
5. Run Query
6. Save to Dashboard

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Journey                         │
└─────────────────────────────────────────────────────────┘

User (Public, No Login)
    ↓
Caddy (Port 80)
    ↓
Django (Port 8000)
    ↓ (Service Account Token)
Superset API
    ↓ (Guest Token)
Django → Frontend
    ↓
User sees embedded dashboard
```

### Components

1. **PostgreSQL**:
   - Stores Django data
   - Stores Superset metadata
   - Stores dummy budget data

2. **Redis**:
   - Superset caching
   - Celery message broker

3. **Apache Superset**:
   - BI platform
   - Dashboard creation
   - Chart visualization

4. **Django**:
   - Public interface
   - Service account integration
   - Guest token generation

5. **Caddy**:
   - Reverse proxy
   - Automatic HTTPS (in production)

## 🔐 Security Flow

### Service Account Token (Backend)

```python
# Django backend menggunakan service account
token = superset.get_service_token()

# Token digunakan untuk:
# - List dashboards
# - Get dashboard info
# - Create guest tokens

# Token TIDAK dikirim ke frontend
```

### Guest Token (Frontend)

```javascript
// Frontend request guest token
const response = await fetch('/api/guest-token/', {
    method: 'POST',
    body: JSON.stringify({ dashboard_uuid })
});

const { guest_token } = await response.json();

// Guest token digunakan untuk embed dashboard
// Lifetime: 5 menit, auto-refresh by SDK
```

## 📂 Project Structure

```
superset-django-2/
├── docker-compose.yml          # Docker Compose configuration
├── init-db.sql                 # Database initialization with dummy data
├── .env                        # Environment variables
├── caddy/
│   └── Caddyfile              # Caddy reverse proxy config
├── superset_config/
│   └── superset_config.py     # Superset configuration
└── django_app/
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    ├── config/                # Django project config
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── dashboards/            # Dashboards app
    │   ├── views.py
    │   ├── urls.py
    │   └── templates/
    │       └── dashboards/
    │           ├── base.html
    │           ├── home.html
    │           ├── dashboard_list.html
    │           ├── dashboard_view.html
    │           └── dashboard_error.html
    └── services/
        └── superset_service.py  # Superset API integration
```

## 🔍 Troubleshooting

> **📖 Full Guide**: Lihat [docs/08-troubleshooting-guide.md](docs/08-troubleshooting-guide.md) untuk panduan lengkap!

### Charts Stuck at "Waiting on PostgreSQL" When Saving

**Symptoms**: Chart preview works but save operation hangs indefinitely

**Root Causes**:
1. Redis connection issues (localhost vs container name)
2. GLOBAL_ASYNC_QUERIES enabled without Celery workers
3. Missing CSRF configuration

**Solution**:
Pastikan konfigurasi ini di `superset_config/superset_config.py`:

```python
# Disable CSRF for API (protected by JWT authentication)
WTF_CSRF_ENABLED = False

# Disable async queries if Celery workers not set up
FEATURE_FLAGS = {
    'GLOBAL_ASYNC_QUERIES': False,  # IMPORTANT!
    # ... other flags
}

# All cache configs must use container hostname 'redis'
CACHE_CONFIG = {
    'CACHE_REDIS_HOST': 'redis',  # NOT 'localhost'
    'CACHE_REDIS_URL': f'redis://redis:6379/1',
}
```

Restart Superset:
```bash
docker compose restart superset
```

### Service Account Login Failed

**Error**: `Failed to authenticate with Superset: 401 UNAUTHORIZED`

**Solution**:
1. Reset service account password:
   ```bash
   docker exec superset superset fab reset-password \
     --username django_service \
     --password your_password_from_env
   ```
2. Verify password matches `.env` file
3. Clear Django cache:
   ```bash
   docker compose restart django
   ```

### Dashboard Not Accessible via Guest Token

**Error**: `Dashboard not accessible via guest token`

**Solution**:
1. Ensure dashboard is **Published** (not Draft)
   - Klik badge "DRAFT" untuk publish
2. Ensure dashboard has **Public** role assigned
   - Settings > Access > Roles > Centang "Public"
3. Verify in Django:
   ```bash
   docker exec django-app python manage.py shell -c "
   from services.superset_service import SupersetService
   s = SupersetService()
   info = s.get_dashboard_visibility_info('your-dashboard-uuid')
   print(info)
   "
   ```

### CSRF Token Errors

**Error**: `The CSRF token is missing` atau `The CSRF session token is missing`

**Solution**:
Disable CSRF di `superset_config.py` (API sudah dilindungi JWT):
```python
WTF_CSRF_ENABLED = False
```

Restart Superset:
```bash
docker compose restart superset
```

### Redis Connection Refused (localhost:6379)

**Error**: `Error 111 connecting to localhost:6379`

**Solution**:
Superset mencoba connect ke localhost instead of container. Update `superset_config.py`:

```python
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')  # NOT 'localhost'

# All cache configs:
CACHE_REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
DATA_CACHE_CONFIG = {..., 'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/2'}
# ... etc for all cache configs
```

### Database Connection Failed

**Error**: `Could not connect to database`

**Solution**:
1. Wait for PostgreSQL to be ready: `docker compose logs postgres`
2. Check credentials in `.env`
3. Test connection:
   ```bash
   docker exec superset-postgres pg_isready -U superset
   ```
4. Recreate containers: `docker compose down && docker compose up -d`

### Port Already in Use

**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution**:
1. Check which process uses the port: `lsof -i :80`
2. Stop the process or change port in `docker-compose.yml`
3. For port 80, you might need sudo

### Superset Container Exits Immediately

**Error**: Container exits with code 1

**Solution**:
1. Check logs: `docker compose logs superset`
2. Common causes:
   - Missing Python dependencies (psycopg2-binary, redis, flask-cors)
   - Configuration errors in superset_config.py
   - Database connection issues
3. Rebuild Superset image:
   ```bash
   docker compose build superset --no-cache
   docker compose up -d superset
   ```

## 🧪 Testing

### Test Service Account Token

```bash
# Access Django container
docker exec -it django-app python manage.py shell

# Test service token
from services.superset_service import SupersetService
superset = SupersetService()
token = superset.get_service_token()
print(f"Service token: {token[:50]}...")

# Test list dashboards
dashboards = superset.list_dashboards()
print(f"Found {len(dashboards)} dashboards")
```

### Test Guest Token Creation

```bash
# In Django shell
dashboard_uuid = "your-dashboard-uuid"
guest_token = superset.create_guest_token(dashboard_uuid)
print(f"Guest token: {guest_token[:50]}...")
```

### Test Public Access

1. Open browser in incognito mode
2. Navigate to http://localhost
3. Should see dashboard list without login
4. Click dashboard to view embedded version

## 📝 Dummy Data

Database include dummy data untuk anggaran pemerintah daerah:

- **8 OPD** (Dinas Pendidikan, Kesehatan, PU, dll)
- **12 Program**
- **25 Kegiatan**
- **7 Kategori Belanja**
- **Rencana Anggaran**: 82 records untuk tahun 2024
- **Realisasi Anggaran**: 82 records dengan varying percentages

### Views Available

- `v_summary_anggaran`: Join semua tables untuk reporting

### Example Queries

```sql
-- Total anggaran per OPD
SELECT nama_opd, SUM(nilai_anggaran) as total_anggaran
FROM v_summary_anggaran
WHERE tahun = 2024
GROUP BY nama_opd
ORDER BY total_anggaran DESC;

-- Persentase realisasi per triwulan
SELECT triwulan,
       SUM(nilai_anggaran) as rencana,
       SUM(nilai_realisasi) as realisasi,
       ROUND((SUM(nilai_realisasi) / SUM(nilai_anggaran) * 100), 2) as persentase
FROM v_summary_anggaran
WHERE tahun = 2024
GROUP BY triwulan
ORDER BY triwulan;
```

## 🔄 Updating

### Update Docker Images

```bash
docker compose pull
docker compose up -d
```

### Update Django Code

```bash
# Stop Django container
docker compose stop django

# Update code (git pull or modify files)

# Rebuild and restart
docker compose build django
docker compose up -d django
```

### Database Migrations

```bash
docker exec -it django-app python manage.py makemigrations
docker exec -it django-app python manage.py migrate
```

## 🛑 Stopping Services

```bash
# Stop all services
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (⚠️ deletes all data)
docker compose down -v
```

## 🚀 Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY values
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use specific CORS origins (not *)
- [ ] Enable HTTPS in Caddy (automatic with domain)
- [ ] Use strong database passwords
- [ ] Enable firewall
- [ ] Regular backups
- [ ] Update Docker images regularly

### Environment Variables for Production

```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SUPERSET_URL=https://superset.yourdomain.com
```

### Caddy with Domain

Update `caddy/Caddyfile`:

```
yourdomain.com {
    reverse_proxy django:8000
}

superset.yourdomain.com {
    reverse_proxy superset:8088
}
```

## 🎛️ Parameters & Filtering

> **📖 Full Guide**: Lihat [docs/07-parameters-and-filtering.md](docs/07-parameters-and-filtering.md) untuk dokumentasi lengkap!

Project ini sudah support multiple filtering methods:

### 1. Dashboard Native Filters (UI-based)

User bisa filter dashboard langsung dari UI tanpa modifikasi code.

**Cara setup**:
1. Edit dashboard > "⚙️" > "Add/Edit filters"
2. Tambahkan filter (contoh: dropdown OPD, slider tahun)
3. Filter otomatis apply ke semua charts

### 2. Jinja Templates dalam SQL Query

Query SQL dinamis menggunakan Jinja2 syntax:

```sql
SELECT opd_nama, SUM(nilai_rencana) as total
FROM v_summary_anggaran
WHERE 1=1
{% if filter_values('opd_filter') %}
    AND opd_nama IN {{ filter_values('opd_filter')|where_in }}
{% endif %}
{% if filter_values('tahun_filter') %}
    AND tahun = {{ filter_values('tahun_filter')[0] }}
{% endif %}
GROUP BY opd_nama
```

### 3. Row Level Security (RLS) via Guest Token

Filter data per-user dari Django backend:

```python
# Contoh: User hanya bisa lihat data dinas mereka
rls_rules = [{
    "clause": "opd_nama = 'Dinas Pendidikan'"
}]

guest_token = superset.create_guest_token(
    dashboard_uuid=dashboard_uuid,
    user_info={"username": "kepala_diknas", ...},
    rls_rules=rls_rules
)
```

**Use cases**:
- Kepala Dinas: hanya lihat data dinasnya
- DPRD: lihat semua tapi filter by tahun
- Public: tanpa RLS, user pilih sendiri via filters

### 4. URL Parameters

Pass parameters via URL query string:

```python
# URL: /dashboards/xxx/?opd=Dinas+Pendidikan&tahun=2024
opd = request.GET.get('opd')
tahun = request.GET.get('tahun')

rls_rules = [{"clause": f"opd_nama = '{opd}' AND tahun = {tahun}"}]
```

## 📚 Documentation

See `docs/` directory for detailed documentation:

- [Apache Superset Overview](docs/01-apache-superset-overview.md)
- [Superset REST API](docs/02-superset-api.md)
- [Authentication & Tokens](docs/03-authentication-tokens.md)
- [Dashboard Permissions](docs/04-dashboard-permissions.md)
- [Django Integration](docs/05-django-integration.md)
- [Implementation Complete](docs/06-implementation-complete.md)
- [Parameters & Filtering](docs/07-parameters-and-filtering.md) 🆕
- [Troubleshooting Guide](docs/08-troubleshooting-guide.md) 🆕

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Apache Superset team
- Django Software Foundation
- Caddy Web Server
- PostgreSQL Global Development Group

## 📞 Support

For issues and questions:

- Check troubleshooting section above
- Review documentation in `docs/` directory
- Create an issue in the repository

---

**Made with ❤️ for transparent government budget visualization**
