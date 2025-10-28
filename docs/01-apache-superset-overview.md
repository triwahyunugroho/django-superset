# Apache Superset Overview

## Apa itu Apache Superset?

Apache Superset adalah **aplikasi web business intelligence modern yang siap untuk enterprise**. Ini adalah platform eksplorasi dan visualisasi data open-source yang dapat menggantikan atau melengkapi tool BI proprietary seperti Tableau, Power BI, atau Looker.

## Fitur Utama

### 1. Visualisasi & Interface

- **No-code Interface**: Membuat chart dengan cepat tanpa coding
- **Web-based SQL Editor**: SQL Lab untuk query kompleks dengan syntax highlighting
- **Berbagai Tipe Visualisasi**:
  - Basic: Bar chart, line chart, pie chart, table
  - Advanced: Heatmap, treemap, sunburst
  - Geographic: Map visualization dengan berbagai projections
  - Time-series: Advanced time series analysis
- **Dashboard Interaktif**: Drag-and-drop dashboard builder dengan filter cross-dashboard

### 2. Data Layer

- **Semantic Layer**:
  - Define custom dimensions dan metrics
  - SQL expressions untuk calculated fields
  - Virtual datasets dari SQL queries
- **Support 40+ Databases**:
  - Data Warehouses: Snowflake, BigQuery, Redshift, Databricks
  - Traditional DB: PostgreSQL, MySQL, Oracle, SQL Server
  - NoSQL: Druid, ClickHouse, Presto, Trino
  - Cloud: AWS Athena, Azure Synapse
- **Caching Layer**:
  - Redis/Memcached integration
  - Query result caching
  - Dashboard metadata caching

### 3. Architecture

- **Cloud-Native Design**:
  - Horizontal scaling
  - Stateless web servers
  - Async query execution dengan Celery
- **Extensible API**:
  - RESTful API dengan OpenAPI spec
  - Programmatic dashboard/chart creation
  - Custom authentication backends
- **Security**:
  - Role-based access control (RBAC)
  - Row-level security (RLS)
  - OAuth, LDAP, OpenID support
  - Column-level permissions

## Instalasi

### Quick Start dengan Docker Compose

Untuk development/testing environment:

```bash
# 1. Clone repository
git clone https://github.com/apache/superset
cd superset

# 2. Checkout versi stable terbaru
git checkout tags/5.0.0

# 3. Start dengan Docker Compose
docker compose -f docker-compose-image-tag.yml up

# 4. Akses Superset
# URL: http://localhost:8088
# Username: admin
# Password: admin
```

**Note**: Docker Compose hanya untuk sandbox/development, tidak untuk production.

### Production Installation

#### Option 1: Kubernetes

```bash
# Install dengan Helm
helm repo add superset https://apache.github.io/superset
helm install superset superset/superset

# Customize dengan values.yaml
helm install superset superset/superset -f values.yaml
```

#### Option 2: PyPI (Python Package)

```bash
# Install Superset
pip install apache-superset

# Initialize database
superset db upgrade

# Create admin user
superset fab create-admin

# Load examples (optional)
superset load_examples

# Initialize
superset init

# Start development server
superset run -p 8088 --with-threads --reload --debugger
```

#### Option 3: Docker Build

```bash
# Build custom image
docker build -t my-superset .

# Run
docker run -d -p 8080:8088 \
  -e "SUPERSET_SECRET_KEY=your-secret-key" \
  my-superset
```

## Configuration

Superset dikonfigurasi melalui file `superset_config.py` atau environment variables.

### Basic Configuration

```python
# superset_config.py

# Secret key untuk session encryption
SECRET_KEY = 'your-secret-key-change-this'

# Database connection (metadata database)
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/superset'

# Async query execution dengan Celery
class CeleryConfig:
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'

CELERY_CONFIG = CeleryConfig
```

### Feature Flags

```python
FEATURE_FLAGS = {
    'DASHBOARD_RBAC': True,           # Dashboard-level permissions
    'EMBEDDED_SUPERSET': True,        # Enable embedding
    'DASHBOARD_NATIVE_FILTERS': True, # Native dashboard filters
    'ENABLE_TEMPLATE_PROCESSING': True,
    'GLOBAL_ASYNC_QUERIES': True,     # Async query execution
}
```

### Security Configuration

```python
# CORS for embedded dashboards
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'origins': ['http://localhost:8000', 'https://yourdomain.com']
}

# Authentication
AUTH_TYPE = AUTH_DB  # or AUTH_OAUTH, AUTH_LDAP, etc.

# Public role (untuk anonymous users)
PUBLIC_ROLE_LIKE = None  # or "Gamma" to give public users Gamma permissions

# Guest token configuration
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = "guest-token-secret"
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes
```

### Cache Configuration

```python
# Redis cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/1'
}

# Data cache
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/2'
}
```

## Database Support

Superset mendukung 40+ database melalui SQLAlchemy dan Python DB-API drivers.

### Kategori Database

#### Data Warehouses
- Amazon Redshift
- Google BigQuery
- Snowflake
- Databricks
- Azure Synapse

#### Traditional Databases
- PostgreSQL
- MySQL / MariaDB
- Oracle
- Microsoft SQL Server
- IBM DB2

#### OLAP / Analytics
- Apache Druid
- ClickHouse
- Apache Pinot
- Apache Kylin

#### Query Engines
- Presto / Trino
- Apache Spark SQL
- Dremio
- Apache Hive

#### Cloud Services
- AWS Athena
- Google Sheets
- Elasticsearch

### Menambahkan Database Connection

#### Via UI:

```
1. Login sebagai Admin
2. Menu: Data > Databases
3. Klik "+ Database"
4. Pilih database type
5. Isi connection details
6. Test connection
7. Save
```

#### Via API:

```python
import requests

url = "http://localhost:8088/api/v1/database/"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

payload = {
    "database_name": "My PostgreSQL",
    "sqlalchemy_uri": "postgresql://user:password@host:5432/dbname",
    "expose_in_sqllab": True,
    "allow_ctas": True,
    "allow_cvas": True,
    "allow_dml": False
}

response = requests.post(url, headers=headers, json=payload)
```

## Use Cases

### 1. Self-Service BI
- Non-technical users dapat explore data dan create charts
- No-code interface untuk basic analytics
- Share dashboards dengan team

### 2. Ad-hoc Analysis
- SQL Lab untuk data exploration
- Export results ke CSV
- Save queries untuk reuse

### 3. Embedded Analytics
- Embed dashboards di aplikasi existing
- White-label dengan custom theming
- Row-level security untuk multi-tenant

### 4. Real-time Monitoring
- Connect ke streaming databases (Druid, ClickHouse)
- Auto-refresh dashboards
- Alerts dan notifications

### 5. Enterprise Reporting
- Scheduled reports via email
- Dashboard screenshots
- CSV/Excel exports

## Architecture Components

### Web Server
- Flask application
- Handles HTTP requests
- Renders UI
- Serves API endpoints

### Metadata Database
- Stores Superset metadata
- Users, roles, permissions
- Dashboard/chart definitions
- Query history

### Cache Layer (Optional)
- Redis/Memcached
- Query results caching
- Metadata caching
- Thumbnail caching

### Celery Workers (Optional)
- Async query execution
- Report/alert generation
- Thumbnail generation
- Cache warming

### Message Queue (for Celery)
- Redis/RabbitMQ
- Task distribution
- Result backend

### Diagram:

```
┌───────────────┐
│   Browser     │
└───────┬───────┘
        │ HTTP/HTTPS
        ▼
┌───────────────┐
│  Load Balancer│
└───────┬───────┘
        │
   ┌────┴────┬────────┐
   ▼         ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│ Web  │ │ Web  │ │ Web  │
│Server│ │Server│ │Server│
└──┬───┘ └──┬───┘ └──┬───┘
   │        │        │
   └────┬───┴────┬───┘
        │        │
        ▼        ▼
   ┌─────────────────┐     ┌──────────────┐
   │ Metadata DB     │     │ Redis Cache  │
   │ (PostgreSQL)    │     │              │
   └─────────────────┘     └──────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │Message Queue │
                          │  (Redis)     │
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
                ┌────────┐  ┌────────┐  ┌────────┐
                │Celery  │  │Celery  │  │Celery  │
                │Worker  │  │Worker  │  │Worker  │
                └────────┘  └────────┘  └────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 ▼
                          ┌──────────────┐
                          │ Data Sources │
                          │ (Various DBs)│
                          └──────────────┘
```

## Roles & Permissions

### Built-in Roles

#### Admin
- Full system access
- User management
- Grant/revoke permissions
- Modify all objects

#### Alpha
- Access all data sources
- Create/edit own dashboards and charts
- Cannot manage users
- Cannot modify other users' objects (by default)

#### Gamma
- View-only role untuk consumers
- Access only assigned data sources
- View assigned dashboards
- Cannot create new content (by default)

#### sql_lab
- Access to SQL Lab
- Run queries
- Save queries
- Must be combined with other roles

#### Public
- For anonymous/logged-out users
- Configured via PUBLIC_ROLE_LIKE
- Used by guest tokens

### Custom Roles

Anda bisa create custom roles untuk specific needs:

```
Finance_Analyst:
- Access to finance datasets only
- Can create charts and dashboards
- Cannot access HR/Sales data

Sales_Viewer:
- View-only access to sales dashboards
- Cannot edit anything
- Cannot access SQL Lab
```

## Best Practices

### 1. Security
- Gunakan strong SECRET_KEY
- Enable HTTPS di production
- Regular security updates
- Audit permissions regularly
- Use RLS untuk multi-tenant scenarios

### 2. Performance
- Enable caching (Redis)
- Use Celery untuk long-running queries
- Optimize database queries
- Use materialized views di database
- Regular cleanup query history

### 3. Scalability
- Deploy multiple web servers
- Deploy multiple Celery workers
- Use load balancer
- Separate metadata DB dari data sources
- Monitor resource usage

### 4. Maintenance
- Regular backups (metadata database)
- Monitor logs
- Set up alerts
- Document custom configurations
- Version control superset_config.py

### 5. User Management
- Use LDAP/OAuth untuk centralized auth
- Create role hierarchy
- Document permission model
- Regular access reviews
- Onboarding documentation

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Test connection manually
superset test-db -d database_id

# Check SQLAlchemy URI format
# Check firewall/network access
# Verify credentials
```

#### Query Timeout
```python
# Increase timeout in superset_config.py
SUPERSET_WEBSERVER_TIMEOUT = 300  # seconds

# Or enable async queries
FEATURE_FLAGS = {'GLOBAL_ASYNC_QUERIES': True}
```

#### Permission Denied
```bash
# Sync permissions
superset init

# Or via UI: Security > List Roles > Sync Permissions
```

#### Slow Dashboard Loading
```python
# Enable caching
CACHE_CONFIG = {...}

# Enable thumbnail cache
THUMBNAIL_CACHE_CONFIG = {...}

# Optimize queries
# Reduce chart count per dashboard
```

## Resources

- [Official Documentation](https://superset.apache.org/docs/6.0.0/)
- [GitHub Repository](https://github.com/apache/superset)
- [Community Slack](https://apache-superset.slack.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/apache-superset)
- [Preset (Managed Superset)](https://preset.io/)

## Next Steps

- [Superset REST API →](./02-superset-api.md)
- [Authentication & Tokens →](./03-authentication-tokens.md)
- [Dashboard Permissions →](./04-dashboard-permissions.md)
- [Django Integration →](./05-django-integration.md)
