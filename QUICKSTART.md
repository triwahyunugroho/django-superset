# Quick Start Guide

Panduan cepat untuk menjalankan Django + Apache Superset Integration.

## 🚀 Start in 5 Minutes

### 1. Clone & Setup

```bash
cd /path/to/superset-django-2

# Copy environment file
cp .env.example .env

# IMPORTANT: Edit .env and change passwords!
nano .env
```

### 2. Start Services

```bash
# Start everything (takes 2-5 minutes first time)
./start.sh

# Wait for all services to be ready
# The script will show you when everything is ready
```

### 3. Create Service Account

```bash
# Enter Superset container
docker exec -it superset bash

# Create service account (use password from .env)
superset fab create-user \
  --username django_service \
  --firstname Django \
  --lastname Service \
  --email service@example.com \
  --password YOUR_PASSWORD_FROM_ENV \
  --role Admin

# Exit
exit
```

### 4. Setup Dashboard in Superset

1. **Open Superset**: http://localhost:8088
   - Login: `admin` / `admin`

2. **Connect Database**:
   - Data → Databases → + Database
   - PostgreSQL
   - Host: `postgres`, Port: `5432`
   - Database: `superset`, User: `superset`
   - Password: (from .env)
   - Test & Save

3. **Create Dataset**:
   - Data → Datasets → + Dataset
   - Database: PostgreSQL
   - Schema: public
   - Table: `v_summary_anggaran`
   - Create

4. **Create Dashboard**:
   - Dashboards → + Dashboard
   - Name: "Dashboard Anggaran 2024"
   - Create charts (examples below)
   - Save

5. **Make Public** ⚠️ IMPORTANT:
   - Click badge **DRAFT** → becomes **PUBLISHED**
   - Click **...** → Edit properties → Access tab
   - Check **Public** role
   - Save

### 5. Test Public Access

```bash
# Open browser (incognito recommended for testing)
# Navigate to: http://localhost

# You should see:
# - Home page
# - Dashboard list (public dashboards)
# - Click to view embedded dashboard
# - NO LOGIN REQUIRED!
```

## 📊 Example Charts

### Chart 1: Anggaran per OPD (Bar)

```
- Type: Bar Chart
- X-axis: nama_opd
- Metric: SUM(nilai_anggaran)
- Filter: tahun = 2024
```

### Chart 2: Realisasi Triwulan (Line)

```
- Type: Line Chart
- X-axis: triwulan
- Metrics: SUM(nilai_realisasi), SUM(nilai_anggaran)
- Filter: tahun = 2024
```

### Chart 3: Kategori Belanja (Pie)

```
- Type: Pie Chart
- Dimension: nama_kategori
- Metric: SUM(nilai_anggaran)
```

## 🛑 Stop Services

```bash
# Stop all services
./stop.sh

# Or manually
docker compose stop
```

## 🔍 Troubleshooting

### Service Account Login Failed

```bash
# Check service account exists
docker exec -it superset superset fab list-users

# Check password
cat .env | grep SUPERSET_SERVICE_PASSWORD

# Recreate if needed
docker exec -it superset bash
superset fab delete-user --username django_service
superset fab create-user ...
```

### Dashboard Not Showing

- ✅ Check status = **PUBLISHED** (not Draft)
- ✅ Check **Public** role assigned
- ✅ Restart: `docker compose restart django`

### Port 80 Already Used

```bash
# Stop conflicting service
sudo systemctl stop apache2
# or
sudo systemctl stop nginx

# Or change port in docker-compose.yml
ports: - "8080:80"
```

## 📚 Full Documentation

See `/docs` folder for complete documentation:

- [README.md](docs/README.md) - Documentation index
- [06-implementation-complete.md](docs/06-implementation-complete.md) - Complete implementation guide

## 🆘 Need Help?

1. Check logs: `docker compose logs -f`
2. Check service status: `docker compose ps`
3. Read troubleshooting: [docs/06-implementation-complete.md](docs/06-implementation-complete.md)
4. Check main README: [README.md](README.md)

## ✅ Checklist

- [ ] .env file configured with secure passwords
- [ ] All services started successfully
- [ ] Service account created in Superset
- [ ] Database connection added
- [ ] Dataset created from v_summary_anggaran
- [ ] Dashboard created with charts
- [ ] Dashboard Published + Public role assigned
- [ ] Tested at http://localhost (no login)

---

**Made with ❤️ for transparent government budget visualization**
