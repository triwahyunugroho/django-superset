# Troubleshooting Guide

Comprehensive troubleshooting guide untuk Django + Superset integration.

## Table of Contents

1. [Setup Issues](#setup-issues)
2. [Superset Issues](#superset-issues)
3. [Django Integration Issues](#django-integration-issues)
4. [Database Issues](#database-issues)
5. [Network & Docker Issues](#network--docker-issues)
6. [Performance Issues](#performance-issues)
7. [Security Issues](#security-issues)

## Setup Issues

### 🔴 Issue: Superset Container Exits Immediately

**Symptoms**:
```bash
docker compose ps
# superset | Exited (1)
```

**Possible Causes**:
1. Missing Python dependencies
2. Configuration errors
3. Database connection issues
4. Port conflicts

**Solution 1: Check Logs**
```bash
docker compose logs superset --tail 50
```

Look for error messages like:
- `ModuleNotFoundError: No module named 'psycopg2'`
- `ModuleNotFoundError: No module named 'redis'`
- `ModuleNotFoundError: No module named 'flask_cors'`

**Solution 2: Missing Dependencies**

If you see `ModuleNotFoundError`, dependencies tidak terinstall dengan benar.

Cek `superset_dockerfile/Dockerfile`:
```dockerfile
FROM apache/superset:latest

USER root

# IMPORTANT: Install ke virtual environment dengan uv
RUN . /app/.venv/bin/activate && \
    uv pip install \
    psycopg2-binary \
    redis \
    flask-cors

USER superset
```

Rebuild container:
```bash
docker compose build superset --no-cache
docker compose up -d superset
```

**Solution 3: Configuration Errors**

Check `superset_config/superset_config.py` for syntax errors:
```bash
python3 -m py_compile superset_config/superset_config.py
```

**Solution 4: Database Not Ready**

Wait for PostgreSQL to be fully ready:
```bash
docker exec superset-postgres pg_isready -U superset
```

### 🔴 Issue: Admin User Not Created

**Symptoms**:
- Can't login with admin/admin
- Error: "User not found"

**Solution 1: Check Entrypoint Script**

Verify `superset_dockerfile/docker-entrypoint.sh` exists and is executable:
```bash
ls -la superset_dockerfile/docker-entrypoint.sh
# Should show: -rwxr-xr-x
```

**Solution 2: Check Environment Variables**

```bash
docker exec superset printenv | grep SUPERSET_ADMIN
```

Should show:
```
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=admin
SUPERSET_ADMIN_EMAIL=admin@example.com
```

**Solution 3: Manually Create Admin User**

```bash
docker exec superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password admin
```

### 🔴 Issue: Service Account Not Working

**Symptoms**:
- Django can't connect to Superset
- Error: `Failed to authenticate with Superset: 401 UNAUTHORIZED`

**Solution 1: Create Service Account**

```bash
docker exec superset superset fab create-user \
  --username django_service \
  --firstname Django \
  --lastname Service \
  --email service@example.com \
  --password your_service_password \
  --role Admin
```

**Solution 2: Reset Password**

Password mungkin tidak match dengan `.env`:

```bash
docker exec superset superset fab reset-password \
  --username django_service \
  --password your_password_from_env
```

**Solution 3: Verify .env Configuration**

Check `django_app/.env` atau environment variables:
```bash
docker exec django-app printenv | grep SUPERSET_SERVICE
```

Should match password in Superset.

## Superset Issues

### 🔴 Issue: Charts Stuck at "Waiting on PostgreSQL" When Saving

**Symptoms**:
- Chart preview works fine
- Data shows in preview
- Save button clicked → hang indefinitely at "Waiting on PostgreSQL"

**Root Causes**:
1. Redis connection issues (localhost vs container hostname)
2. `GLOBAL_ASYNC_QUERIES` enabled without Celery workers
3. CSRF token issues
4. Missing cache configurations

**Solution: Complete Fix**

Edit `superset_config/superset_config.py`:

```python
# 1. Disable CSRF (API protected by JWT authentication)
WTF_CSRF_ENABLED = False

# 2. Disable async queries (requires Celery workers)
FEATURE_FLAGS = {
    'GLOBAL_ASYNC_QUERIES': False,  # CRITICAL!
    'DASHBOARD_RBAC': True,
    'EMBEDDED_SUPERSET': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_FILTERS_EXPERIMENTAL': True,
    'ALLOW_FULL_CSV_EXPORT': True,
}

# 3. Fix Redis hostname (NOT localhost!)
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')  # NOT 'localhost'
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

# 4. ALL cache configs MUST include CACHE_REDIS_URL
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',  # REQUIRED!
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 2,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/2',  # REQUIRED!
}

RESULTS_BACKEND = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 3,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/3',  # REQUIRED!
}

THUMBNAIL_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 4,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/4',  # REQUIRED!
}

FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 5,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/5',  # REQUIRED!
}

EXPLORE_FORM_DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 6,
    'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/6',  # REQUIRED!
}

# 5. Configure async queries Redis (even when disabled)
GLOBAL_ASYNC_QUERIES_REDIS_CONFIG = {
    'port': REDIS_PORT,
    'host': REDIS_HOST,
    'db': 0,
}
```

Restart Superset:
```bash
docker compose restart superset
```

Wait 30 seconds for initialization, then test chart save.

### 🔴 Issue: CSRF Token Errors

**Symptoms**:
- Error: `400 Bad Request: The CSRF token is missing`
- Error: `400 Bad Request: The CSRF session token is missing`
- Guest token creation fails

**Root Cause**:
Superset expects CSRF tokens for POST requests, but JWT authentication already provides security.

**Solution**:

Disable CSRF in `superset_config.py`:
```python
WTF_CSRF_ENABLED = False
```

Restart:
```bash
docker compose restart superset
```

### 🔴 Issue: Redis Connection Refused (localhost:6379)

**Symptoms**:
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Root Cause**:
Superset trying to connect to `localhost:6379` instead of container hostname `redis:6379`.

**Solution**:

Update ALL Redis configurations in `superset_config.py`:

```python
# Use environment variable or default to 'redis'
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')  # NOT 'localhost'

# Every cache config needs CACHE_REDIS_URL
CACHE_REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
```

Restart:
```bash
docker compose restart superset
```

Verify Redis connection:
```bash
docker exec superset python -c "
import redis
r = redis.Redis(host='redis', port=6379)
print('Redis ping:', r.ping())
"
```

Should output: `Redis ping: True`

## Django Integration Issues

### 🔴 Issue: Dashboard Not Accessible via Guest Token

**Symptoms**:
- Dashboard shows in Superset but not in Django list
- Error: `Dashboard not accessible via guest token`
- Error: `Dashboard is in Draft mode`

**Root Cause**:
Dashboard needs to be **Published** with **Public** role.

**Solution**:

1. **Publish Dashboard**:
   - Open dashboard in Superset
   - Click badge "DRAFT" → Change to "PUBLISHED"
   - Or: Settings > Klik toggle "Published"

2. **Add Public Role**:
   - Dashboard settings > Access tab
   - Roles section > Centang "Public"
   - Save

3. **Verify in Django**:
```bash
docker exec django-app python manage.py shell -c "
from services.superset_service import SupersetService
s = SupersetService()

# Check dashboard visibility
info = s.get_dashboard_visibility_info('your-dashboard-uuid')
print(f'Published: {info[\"published\"]}')
print(f'Has Public Role: {info[\"has_public_role\"]}')
print(f'Guest Token Accessible: {info[\"guest_token_accessible\"]}')

# List public dashboards
public = s.list_public_dashboards()
print(f'Found {len(public)} public dashboards')
"
```

### 🔴 Issue: Service Token Authentication Failed

**Symptoms**:
```
Failed to authenticate with Superset: 401 Client Error: UNAUTHORIZED
```

**Solutions**:

**Check 1: Service account exists**
```bash
docker exec superset superset fab list-users | grep django_service
```

**Check 2: Password matches**
```bash
# Check Django env
docker exec django-app printenv SUPERSET_SERVICE_PASSWORD

# Reset if needed
docker exec superset superset fab reset-password \
  --username django_service \
  --password your_password_from_env
```

**Check 3: Superset is accessible**
```bash
docker exec django-app curl -f http://superset:8088/health
# Should output: OK
```

**Check 4: Clear Django cache**
```bash
docker compose restart django
```

### 🔴 Issue: CORS Errors in Browser

**Symptoms**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:

Check `superset_config.py`:
```python
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': [
        'http://localhost',
        'http://localhost:80',
        'http://localhost:8000',
        'http://localhost:8088',
        'http://caddy',
        'http://django',
        '*',  # Allow all for development (restrict in production!)
    ]
}
```

Restart Superset:
```bash
docker compose restart superset
```

## Database Issues

### 🔴 Issue: Database Connection Failed

**Symptoms**:
```
Could not connect to database
sqlalchemy.exc.OperationalError
```

**Solutions**:

**Check 1: PostgreSQL is running**
```bash
docker compose ps postgres
# Should show: Up

docker exec superset-postgres pg_isready -U superset
# Should output: /var/run/postgresql:5432 - accepting connections
```

**Check 2: Wait for PostgreSQL to be ready**
```bash
# PostgreSQL needs time to initialize on first run
docker compose logs postgres --tail 50
# Look for: "database system is ready to accept connections"
```

**Check 3: Test connection**
```bash
docker exec superset-postgres psql -U superset -c "SELECT 1"
```

**Check 4: Verify credentials**

Check `.env` file:
```bash
POSTGRES_USER=superset
POSTGRES_PASSWORD=your_password
POSTGRES_DB=superset
```

Check Superset config:
```bash
docker exec superset printenv SUPERSET_DATABASE_URI
```

Should be: `postgresql+psycopg2://superset:password@postgres:5432/superset`

**Check 5: Recreate containers**
```bash
docker compose down
docker compose up -d
```

### 🔴 Issue: Database Init SQL Not Executed

**Symptoms**:
- Table `v_summary_anggaran` not found
- No dummy data in database

**Solution**:

1. **Check if SQL was executed**:
```bash
docker exec superset-postgres psql -U superset -c "\dt"
# Should show tables: opd, program, kegiatan, etc.
```

2. **Manually execute init SQL**:
```bash
docker cp init-db.sql superset-postgres:/tmp/
docker exec superset-postgres psql -U superset -f /tmp/init-db.sql
```

3. **Recreate database** (⚠️ deletes all data):
```bash
docker compose down -v  # Remove volumes
docker compose up -d
```

## Network & Docker Issues

### 🔴 Issue: Port Already in Use

**Symptoms**:
```
Bind for 0.0.0.0:80 failed: port is already allocated
```

**Solution 1: Find process using port**
```bash
# Linux/Mac
lsof -i :80

# Windows
netstat -ano | findstr :80
```

**Solution 2: Stop process or change port**

Change port in `docker-compose.yml`:
```yaml
caddy:
  ports:
    - "8080:80"  # Change 80 to 8080
```

**Solution 3: Use sudo for port 80**
```bash
sudo docker compose up -d
```

### 🔴 Issue: Containers Can't Communicate

**Symptoms**:
- Django can't reach Superset
- Superset can't reach PostgreSQL
- Error: `Name or service not known`

**Solution 1: Check network**
```bash
docker network ls
# Should show: superset-network

docker network inspect superset-network
# Should show all containers
```

**Solution 2: Use container hostnames**

NOT: `localhost`, `127.0.0.1`, `0.0.0.0`

USE: Container names from docker-compose.yml
- `postgres` for PostgreSQL
- `redis` for Redis
- `superset` for Superset
- `django` for Django

**Solution 3: Test connection**
```bash
# From Django to Superset
docker exec django-app curl -f http://superset:8088/health

# From Superset to PostgreSQL
docker exec superset pg_isready -h postgres -p 5432 -U superset

# From Superset to Redis
docker exec superset redis-cli -h redis ping
```

### 🔴 Issue: Docker Out of Disk Space

**Symptoms**:
```
no space left on device
```

**Solution**:

```bash
# Clean up unused images
docker system prune -a

# Clean up volumes (⚠️ deletes data)
docker volume prune

# Check disk usage
docker system df
```

## Performance Issues

### 🔴 Issue: Dashboard Loads Slowly

**Symptoms**:
- Dashboard takes >10 seconds to load
- Charts timeout

**Solutions**:

**Solution 1: Enable Redis caching** (already configured)

Verify Redis is used:
```bash
docker exec superset python -c "
from superset import cache
print('Cache type:', cache.cache._cache.__class__.__name__)
"
```

**Solution 2: Add database indexes**

For columns used in filters and GROUP BY:
```sql
CREATE INDEX idx_opd_nama ON v_summary_anggaran(opd_nama);
CREATE INDEX idx_tahun ON v_summary_anggaran(tahun);
CREATE INDEX idx_triwulan ON v_summary_anggaran(triwulan);
```

**Solution 3: Optimize queries**

- Use WHERE instead of HAVING
- Avoid SELECT *
- Limit result size
- Use aggregations in database, not application

**Solution 4: Increase cache timeout**

In `superset_config.py`:
```python
DATA_CACHE_CONFIG = {
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    # ...
}
```

### 🔴 Issue: Memory Issues

**Symptoms**:
- Containers killed by OOM
- `docker ps` shows containers restarting

**Solution**:

Increase Docker memory allocation:
- Docker Desktop → Settings → Resources → Memory → 8GB minimum

Or limit individual containers in `docker-compose.yml`:
```yaml
superset:
  deploy:
    resources:
      limits:
        memory: 2G
```

## Security Issues

### 🔴 Issue: Default Passwords in Production

**⚠️ CRITICAL**: Never use default passwords in production!

**Solution**:

1. **Change all passwords in `.env`**:
```bash
# Generate strong passwords
openssl rand -base64 32

# Update .env
POSTGRES_PASSWORD=generated_strong_password_1
SUPERSET_SECRET_KEY=generated_strong_password_2
DJANGO_SECRET_KEY=generated_strong_password_3
SUPERSET_SERVICE_PASSWORD=generated_strong_password_4
GUEST_TOKEN_JWT_SECRET=generated_strong_password_5
SUPERSET_ADMIN_PASSWORD=generated_strong_password_6
```

2. **Recreate containers**:
```bash
docker compose down
docker compose up -d
```

3. **Update service account password**:
```bash
docker exec superset superset fab reset-password \
  --username django_service \
  --password new_service_password
```

### 🔴 Issue: SQL Injection in RLS

**⚠️ CRITICAL**: URL parameters can cause SQL injection!

**Bad**:
```python
opd = request.GET.get('opd')
rls = [{"clause": f"opd_nama = '{opd}'"}]  # VULNERABLE!
```

**Good**:
```python
import re

def sanitize_param(value, pattern=r'^[a-zA-Z0-9\s]+$'):
    if not re.match(pattern, value):
        raise ValueError("Invalid parameter")
    return value

opd = sanitize_param(request.GET.get('opd', ''))
rls = [{"clause": f"opd_nama = '{opd}'"}]  # SAFE
```

## Diagnostic Commands

### Check All Services Status

```bash
# Quick status
docker compose ps

# Detailed info
docker compose ps -a

# Service logs
docker compose logs superset --tail 50
docker compose logs django --tail 50
docker compose logs postgres --tail 50
```

### Test Service Connectivity

```bash
# Test Superset health
curl http://localhost:8088/health

# Test Django
curl http://localhost:8000

# Test Caddy
curl http://localhost

# Test PostgreSQL
docker exec superset-postgres pg_isready -U superset

# Test Redis
docker exec superset-redis redis-cli ping
```

### Django Shell Tests

```bash
docker exec -it django-app python manage.py shell
```

```python
# Test Superset service
from services.superset_service import SupersetService
s = SupersetService()

# Test authentication
token = s.get_service_token()
print(f"Token: {token[:50]}...")

# Test dashboards
dashboards = s.list_dashboards()
print(f"Found {len(dashboards)} dashboards")

# Test guest token
guest_token = s.create_guest_token(
    dashboard_uuid='your-uuid',
    user_info={"username": "test", "first_name": "Test", "last_name": "User"}
)
print(f"Guest token: {guest_token[:50]}...")
```

### Superset Shell Tests

```bash
docker exec -it superset superset shell
```

```python
# List users
from superset import security_manager
users = security_manager.get_all_users()
for u in users:
    print(f"{u.username} - {[r.name for r in u.roles]}")

# List dashboards
from superset import db
from superset.models.dashboard import Dashboard
dashboards = db.session.query(Dashboard).all()
for d in dashboards:
    print(f"{d.dashboard_title} - Published: {d.published}")
```

## Getting Help

If issues persist:

1. **Check documentation**: Read all docs in `docs/` folder
2. **Check logs**: `docker compose logs -f`
3. **Search GitHub Issues**: Check if issue already reported
4. **Create issue**: Provide:
   - Exact error message
   - Steps to reproduce
   - Output of diagnostic commands
   - Docker and OS versions

---

**Related Docs**:
- [Parameters & Filtering](07-parameters-and-filtering.md)
- [Django Integration](05-django-integration.md)
- [Implementation Complete](06-implementation-complete.md)
