# Django + Apache Superset Integration

Integrasi sederhana Django dengan Apache Superset untuk menampilkan dashboard anggaran pemerintah daerah yang dapat diakses publik tanpa login.

## 🎯 Fitur

- ✅ **Public Access**: Dashboard dapat diakses tanpa login
- ✅ **Service Account Token**: Backend Django menggunakan service account untuk API calls
- ✅ **Guest Token**: Frontend menggunakan guest token untuk embed dashboard
- ✅ **Dashboard Management**: Pembuat dashboard dapat menentukan visibility (public/private)
- ✅ **Docker Compose**: Setup lengkap dengan satu command
- ✅ **PostgreSQL**: Database untuk Django dan Superset
- ✅ **Caddy**: Web server modern dengan auto-HTTPS
- ✅ **Dummy Data**: Data anggaran pemerintah daerah siap pakai

## 📋 Prerequisites

- Docker & Docker Compose
- Git
- 8GB RAM minimum
- Port 80, 5432, 6379, 8000, 8088 available

## 🚀 Quick Start

> **⚡ Super Quick Start**: Lihat [QUICKSTART.md](QUICKSTART.md) untuk panduan 5 menit!
>
> **📚 Complete Guide**: Lihat [docs/06-implementation-complete.md](docs/06-implementation-complete.md) untuk dokumentasi lengkap!

### 1. Clone Repository

```bash
git clone <repository-url>
cd superset-django-2
```

### 2. Copy Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file dan ubah password/secret keys sesuai kebutuhan:

```bash
# .env
POSTGRES_PASSWORD=your_secure_password
SUPERSET_SECRET_KEY=your_superset_secret
DJANGO_SECRET_KEY=your_django_secret
SUPERSET_SERVICE_PASSWORD=your_service_password
GUEST_TOKEN_JWT_SECRET=your_guest_token_secret
```

### 3. Start Services

```bash
docker compose up -d
```

Tunggu beberapa menit untuk initial setup. Monitor logs:

```bash
docker compose logs -f
```

### 4. Create Service Account in Superset

Setelah Superset ready, buat service account untuk Django:

```bash
# Exec into Superset container
docker exec -it superset bash

# Create service account
superset fab create-user \
  --username django_service \
  --firstname Django \
  --lastname Service \
  --email service@example.com \
  --password django_service_password_change_this \
  --role Admin

# Exit container
exit
```

**Penting**: Password harus sama dengan `SUPERSET_SERVICE_PASSWORD` di `.env` file.

### 5. Access Applications

- **Django (Public)**: http://localhost
- **Superset (Admin)**: http://localhost:8088
  - Username: `admin`
  - Password: `admin` (atau sesuai `SUPERSET_ADMIN_PASSWORD`)

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

### Service Account Login Failed

**Error**: `Failed to authenticate with Superset`

**Solution**:
1. Check service account exists in Superset
2. Verify password matches `.env` file
3. Check Superset is running: `docker compose ps`
4. Check logs: `docker compose logs superset`

### Dashboard Not Accessible via Guest Token

**Error**: `Dashboard not accessible via guest token`

**Solution**:
1. Ensure dashboard is **Published** (not Draft)
2. Ensure dashboard has **Public** role assigned
3. Enable feature flags in `superset_config.py`:
   ```python
   FEATURE_FLAGS = {
       'DASHBOARD_RBAC': True,
       'EMBEDDED_SUPERSET': True,
   }
   ```
4. Restart Superset: `docker compose restart superset`

### CORS Error in Browser Console

**Error**: `Access-Control-Allow-Origin`

**Solution**:
Check `superset_config.py`:
```python
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'origins': ['*'],  # Or specific domain
}
```

### Database Connection Failed

**Error**: `Could not connect to database`

**Solution**:
1. Wait for PostgreSQL to be ready: `docker compose logs postgres`
2. Check credentials in `.env`
3. Recreate containers: `docker compose down && docker compose up -d`

### Port Already in Use

**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution**:
1. Check which process uses the port: `lsof -i :80`
2. Stop the process or change port in `docker-compose.yml`
3. For port 80, you might need sudo

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

## 📚 Documentation

See `docs/` directory for detailed documentation:

- [Apache Superset Overview](docs/01-apache-superset-overview.md)
- [Superset REST API](docs/02-superset-api.md)
- [Authentication & Tokens](docs/03-authentication-tokens.md)
- [Dashboard Permissions](docs/04-dashboard-permissions.md)
- [Django Integration](docs/05-django-integration.md)

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
