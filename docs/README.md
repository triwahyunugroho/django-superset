# Dokumentasi Integrasi Django dengan Apache Superset

Dokumentasi lengkap hasil riset dan implementasi integrasi Django dengan Apache Superset.

## Daftar Isi

1. [Apache Superset Overview](./01-apache-superset-overview.md)
   - Apa itu Apache Superset
   - Fitur-fitur utama
   - Instalasi dan setup
   - Database yang didukung

2. [Superset REST API](./02-superset-api.md)
   - Struktur API
   - Authentication
   - Endpoint-endpoint utama
   - Contoh penggunaan

3. [Authentication & Token Management](./03-authentication-tokens.md)
   - Service Account Token
   - Guest Token
   - Perbedaan dan use case
   - Best practices

4. [Dashboard Visibility & Permissions](./04-dashboard-permissions.md)
   - Draft vs Published
   - Dashboard RBAC
   - Role-based access control
   - Public vs Private dashboard

5. [Django + Superset Integration Guide](./05-django-integration.md)
   - Architecture overview
   - Implementation lengkap
   - Backend (Django)
   - Frontend (Templates & JavaScript)
   - Configuration

6. [**Implementasi Lengkap (Complete Implementation)**](./06-implementation-complete.md) ⭐
   - Docker Compose setup
   - Database dengan dummy data anggaran
   - Service Account + Guest Token
   - Public access tanpa login
   - Dashboard visibility control
   - Production deployment guide
   - Troubleshooting lengkap

## Quick Start

### 🚀 Implementasi Lengkap Tersedia!

**Implementasi complete dengan Docker Compose sudah tersedia!**

Lihat [**Implementasi Lengkap (Complete Implementation)**](./06-implementation-complete.md) untuk:
- ✅ Docker Compose setup (PostgreSQL, Redis, Superset, Django, Caddy)
- ✅ Database dengan dummy data anggaran pemerintah daerah
- ✅ Service Account + Guest Token implementation
- ✅ Public access tanpa login
- ✅ Dashboard visibility control
- ✅ Production deployment guide

### One-Command Start

```bash
# Clone project
cd superset-django-2

# Edit environment variables
cp .env.example .env
nano .env

# Start everything!
./start.sh

# Access:
# - Public: http://localhost
# - Superset Admin: http://localhost:8088
```

Untuk setup manual atau development without Docker, lihat panduan di bawah:

### Prerequisites (Manual Setup)

- Python 3.8+
- Django 3.2+
- Apache Superset 6.0.0+
- Docker & Docker Compose (recommended)

### Setup Superset (Development - Manual)

```bash
# Clone Superset repository
git clone https://github.com/apache/superset
cd superset

# Checkout latest stable version
git checkout tags/5.0.0

# Start with Docker Compose
docker compose -f docker-compose-image-tag.yml up

# Access Superset
# URL: http://localhost:8088
# Username: admin
# Password: admin
```

### Setup Django Project (Manual)

```bash
# Install dependencies
pip install requests python-dotenv

# Create .env file
cat > .env << EOF
SUPERSET_URL=http://localhost:8088
SUPERSET_SERVICE_USER=django_service_account
SUPERSET_SERVICE_PASSWORD=your_secure_password
EOF

# Run Django
python manage.py runserver
```

## Key Concepts

### Service Account Token
Token yang digunakan oleh Django backend untuk berkomunikasi dengan Superset API (list dashboard, manage resources, create guest token).

### Guest Token
Token sementara (5 menit) yang digunakan untuk embed dashboard di frontend tanpa perlu login ke Superset.

### Workflow
```
User → Django → Superset API (service token)
                    ↓
               Guest Token
                    ↓
Frontend ← Django ← Guest Token
    ↓
Embed Dashboard (guest token)
```

## Architecture

```
┌─────────────────────┐
│   Django Frontend   │
│   (User Interface)  │
└──────────┬──────────┘
           │ HTTP Request
           ▼
┌─────────────────────┐
│   Django Backend    │
│   - Views           │
│   - SupersetService │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│   Apache Superset   │
│   - Dashboards      │
│   - Charts          │
│   - Datasets        │
└─────────────────────┘
```

## Use Cases

### 1. List Dashboard untuk User
Django menggunakan service account token untuk mengambil list dashboard dari Superset, kemudian filter berdasarkan permission user Django.

### 2. Embed Dashboard
User klik dashboard → Django buat guest token → Frontend embed dashboard dengan guest token → User lihat dashboard interaktif.

### 3. Dashboard Management
Admin bisa manage dashboard visibility (public/private) melalui Django admin interface.

## Security Considerations

1. **Service Account Credentials**
   - Simpan di environment variables
   - Jangan commit ke git
   - Gunakan strong password

2. **Guest Token**
   - Short-lived (5 menit)
   - Limited scope (specific dashboard only)
   - Auto-refresh by SDK

3. **Dashboard Permissions**
   - Gunakan DASHBOARD_RBAC untuk granular control
   - Review role permissions regularly
   - Audit access logs

## Troubleshooting

### Guest Token Error 403
- Pastikan dashboard status = Published
- Pastikan Public role punya akses ke dashboard atau datasets
- Check FEATURE_FLAGS: EMBEDDED_SUPERSET = True

### CORS Error
- Enable CORS di superset_config.py
- Tambahkan Django domain ke CORS_OPTIONS

### Token Expired
- Guest token expire otomatis setiap 5 menit
- SDK otomatis refresh, pastikan fetchGuestToken function bekerja

## Resources

- [Apache Superset Documentation](https://superset.apache.org/docs/6.0.0/)
- [Superset API](https://superset.apache.org/docs/6.0.0/api)
- [Superset GitHub](https://github.com/apache/superset)
- [Embedded SDK](https://www.npmjs.com/package/@superset-ui/embedded-sdk)

## Contributors

Dokumentasi ini dibuat berdasarkan riset Apache Superset versi 6.0.0.

## License

Apache License 2.0
