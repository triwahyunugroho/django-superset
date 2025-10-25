# Superset Django Integration - Anggaran Daerah

Project sederhana yang mengintegrasikan Apache Superset dan Django untuk sistem informasi anggaran pemerintah daerah di Indonesia.

## Tech Stack

- **Django 4.2.7** - Backend framework
- **Apache Superset 3.0.0** - Data visualization & BI platform
- **PostgreSQL 15** - Database
- **Redis 7** - Cache & message broker
- **Caddy 2** - Reverse proxy & web server
- **Docker Compose** - Container orchestration
- **django-superset-integration 0.1.17** - Package untuk integrasi Superset dengan Django

## Struktur Project

```
superset-django/
├── docker-compose.yml          # Konfigurasi Docker Compose
├── Caddyfile                   # Konfigurasi Caddy reverse proxy
├── init-db.sql                 # SQL script untuk inisialisasi database
├── .env.example                # Contoh environment variables
├── README.md                   # Dokumentasi ini
│
├── django/                     # Django application
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── config/                 # Django settings & config
│   ├── budget/                 # App untuk anggaran daerah
│   │   ├── models.py          # Database models
│   │   ├── admin.py           # Django admin configuration
│   │   ├── views.py           # Views
│   │   ├── urls.py            # URL routing
│   │   └── management/        # Custom management commands
│   │       └── commands/
│   │           └── load_dummy_data.py
│   └── templates/             # HTML templates
│
└── superset/                   # Apache Superset configuration
    ├── Dockerfile
    └── superset_config.py
```

## Database Models

Project ini memiliki 6 model database untuk anggaran pemerintah daerah:

1. **Provinsi** - Data provinsi di Indonesia
2. **KabupatenKota** - Data kabupaten/kota
3. **ProgramKegiatan** - Program dan kegiatan pemerintah
4. **JenisAnggaran** - Jenis/kategori anggaran (Pegawai, Barang & Jasa, Modal, dll)
5. **AnggaranDaerah** - Data anggaran daerah (pagu, realisasi, status)
6. **RealisasiBulanan** - Realisasi anggaran per bulan

## Prerequisites

- Docker & Docker Compose
- Git
- Port 80, 443, 5432, 6379, 8000, 8088 tersedia

## Installation & Setup

### 1. Clone/Download Project

```bash
cd /home/kirinyakanan/Documents/projects/superset-django
```

### 2. Generate Encryption Key

Buka Python shell dan generate Fernet key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Copy output dan simpan di environment variable `FERNET_KEY`.

### 3. Setup Environment Variables (Opsional)

```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
```

### 4. Build dan Start Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Lihat logs
docker-compose logs -f
```

### 5. Setup Django

```bash
# Masuk ke container Django
docker-compose exec django bash

# Jalankan migrasi database
python manage.py migrate

# Load dummy data
python manage.py load_dummy_data

# Buat superuser untuk Django Admin
python manage.py createsuperuser

# Exit dari container
exit
```

### 6. Akses Aplikasi

- **Django App**: http://localhost
- **Django Admin**: http://localhost/admin
- **Apache Superset**: http://localhost/superset
- **PostgreSQL**: localhost:5432

**Default Credentials:**
- Superset: username `admin`, password `admin`
- Django: sesuai superuser yang dibuat

## Cara Menggunakan

### 1. Setup Database Connection di Superset

1. Buka http://localhost/superset
2. Login dengan admin/admin
3. Go to **Settings > Database Connections**
4. Klik **+ Database**
5. Pilih PostgreSQL
6. Isi connection string:
   ```
   postgresql://superset_user:superset_password@postgres:5432/superset_db
   ```
7. Test connection dan simpan

### 2. Buat Dataset di Superset

1. Go to **Data > Datasets**
2. Klik **+ Dataset**
3. Pilih database yang baru dibuat
4. Pilih schema `public`
5. Pilih tabel (misalnya: `anggaran_daerah`, `provinsi`, dll)
6. Simpan

### 3. Buat Chart & Dashboard

1. Dari dataset, klik **Create Chart**
2. Pilih chart type (Bar Chart, Pie Chart, Table, dll)
3. Konfigurasi metrics dan dimensions
4. Simpan chart
5. Buat dashboard baru dan tambahkan chart

### 4. Embed Dashboard ke Django

1. Catat Dashboard ID dari URL Superset (contoh: `/superset/dashboard/1/`)
2. Buka Django Admin: http://localhost/admin
3. Tambah **Superset Instance**:
   - Name: `Superset Server`
   - URL: `http://superset:8088`
   - Username: `admin`
   - Password: `admin`
4. Tambah **Superset Dashboard**:
   - Instance: pilih Superset Server
   - Dashboard ID: masukkan ID dari step 1
   - Name: `Dashboard Anggaran Daerah`
5. Buka http://localhost/dashboard/ untuk melihat embedded dashboard

## Data Dummy

Dummy data yang di-generate mencakup:

- **7 Provinsi** (DKI Jakarta, Jawa Barat, Jawa Tengah, DIY, Jawa Timur, Bali, Sulawesi Selatan)
- **17 Kabupaten/Kota**
- **13 Program Kegiatan** (Pendidikan, Kesehatan, Infrastruktur, dll)
- **12 Jenis Anggaran**
- **Ratusan data anggaran** untuk tahun 2023-2025
- **Ribuan data realisasi bulanan**

## Management Commands

```bash
# Load dummy data
python manage.py load_dummy_data

# Membuat migrasi
python manage.py makemigrations

# Jalankan migrasi
python manage.py migrate
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Execute command in container
docker-compose exec [service_name] [command]
```

## Troubleshooting

### Superset tidak bisa start
- Check logs: `docker-compose logs superset`
- Pastikan database PostgreSQL sudah siap
- Coba restart: `docker-compose restart superset`

### Django tidak bisa konek ke database
- Pastikan service postgres sudah running
- Check environment variables di docker-compose.yml
- Coba restart: `docker-compose restart django`

### Dashboard tidak muncul di Django
- Pastikan SupersetInstance dan SupersetDashboard sudah dibuat di Django Admin
- Pastikan FERNET_KEY sudah di-set dengan benar
- Check browser console untuk error
- Pastikan CORS settings di Superset sudah benar

### Port sudah digunakan
- Ubah port mapping di docker-compose.yml
- Contoh: ubah `"8000:8000"` menjadi `"8001:8000"`

## Features

- ✅ Full integration Django & Apache Superset
- ✅ Database dummy anggaran pemerintah daerah
- ✅ Docker Compose setup
- ✅ Reverse proxy dengan Caddy
- ✅ Django Admin interface
- ✅ Embedded Superset dashboard
- ✅ RESTful API ready
- ✅ Multi-tahun anggaran (2023-2025)
- ✅ Tracking realisasi bulanan
- ✅ Kategorisasi lengkap anggaran

## Development

Untuk development, Anda bisa:

1. Edit kode Django di folder `django/`
2. Changes akan auto-reload (DEBUG=True)
3. Tambah models baru di `budget/models.py`
4. Buat migrations: `python manage.py makemigrations`
5. Jalankan migrations: `python manage.py migrate`

## Production Considerations

Untuk production deployment:

- [ ] Ubah semua secret keys dan passwords
- [ ] Set DEBUG=False
- [ ] Gunakan proper ALLOWED_HOSTS
- [ ] Setup HTTPS/SSL di Caddy
- [ ] Gunakan volume untuk database persistence
- [ ] Setup backup untuk PostgreSQL
- [ ] Configure proper CORS settings
- [ ] Use gunicorn dengan lebih banyak workers
- [ ] Setup monitoring & logging
- [ ] Implement rate limiting

## License

MIT License - Free to use for learning and development purposes.

## Contributors

Developed with Claude Code - AI-powered coding assistant.
