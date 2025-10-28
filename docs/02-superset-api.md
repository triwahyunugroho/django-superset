# Superset REST API

## Overview

Superset menyediakan **public REST API** yang mengikuti **OpenAPI specification** dan didokumentasikan menggunakan **Swagger UI**.

### Key Characteristics

- **Version**: API v1
- **Standard**: RESTful, OpenAPI compliant
- **Authentication**: JWT (JSON Web Token)
- **Format**: JSON request/response
- **Documentation**: Interactive Swagger UI

### Accessing API Documentation

#### Interactive Swagger UI

Setiap Superset instance menyediakan interactive API documentation:

```
http://your-superset-domain/swagger/v1
```

Contoh untuk local development:
```
http://localhost:8088/swagger/v1
```

Di Swagger UI, Anda bisa:
- Melihat semua available endpoints
- Mencoba API calls secara langsung
- Melihat request/response schemas
- Test authentication

## Authentication

### 1. Login untuk Mendapatkan Access Token

**Endpoint**: `POST /api/v1/security/login`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/security/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin",
    "provider": "db",
    "refresh": true
  }'
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Menggunakan Access Token

Semua API calls harus menyertakan access token di header:

```bash
curl -X GET "http://localhost:8088/api/v1/dashboard/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Refresh Token

**Endpoint**: `POST /api/v1/security/refresh`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/security/refresh" \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

### 4. CSRF Token (untuk web forms)

**Endpoint**: `GET /api/v1/security/csrf_token/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/security/csrf_token/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Core API Endpoints

### Dashboards

#### List All Dashboards

**Endpoint**: `GET /api/v1/dashboard/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/dashboard/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "count": 10,
  "ids": [1, 2, 3],
  "result": [
    {
      "id": 1,
      "uuid": "abc-123-def-456",
      "dashboard_title": "Sales Dashboard",
      "url": "/superset/dashboard/1/",
      "published": true,
      "owners": [
        {
          "id": 1,
          "username": "admin",
          "first_name": "Admin",
          "last_name": "User"
        }
      ],
      "roles": [
        {
          "id": 1,
          "name": "Public"
        }
      ],
      "position_json": "...",
      "css": "",
      "json_metadata": "...",
      "thumbnail_url": "/api/v1/dashboard/1/thumbnail/..."
    }
  ]
}
```

#### Get Dashboard Detail

**Endpoint**: `GET /api/v1/dashboard/{id_or_slug}`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/dashboard/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Dashboard

**Endpoint**: `POST /api/v1/dashboard/`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/dashboard/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard_title": "New Dashboard",
    "published": false,
    "owners": [1]
  }'
```

#### Update Dashboard

**Endpoint**: `PUT /api/v1/dashboard/{id}`

**Request**:
```bash
curl -X PUT "http://localhost:8088/api/v1/dashboard/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard_title": "Updated Dashboard",
    "published": true
  }'
```

#### Delete Dashboard

**Endpoint**: `DELETE /api/v1/dashboard/{id}`

**Request**:
```bash
curl -X DELETE "http://localhost:8088/api/v1/dashboard/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Charts

#### List All Charts

**Endpoint**: `GET /api/v1/chart/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/chart/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "count": 50,
  "result": [
    {
      "id": 1,
      "slice_name": "Sales by Region",
      "viz_type": "bar",
      "datasource_id": 1,
      "datasource_type": "table",
      "params": "...",
      "cache_timeout": 3600,
      "owners": [...]
    }
  ]
}
```

#### Get Chart Detail

**Endpoint**: `GET /api/v1/chart/{id}`

#### Get Chart Data

**Endpoint**: `GET /api/v1/chart/{id}/data/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/chart/1/data/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response** (actual chart data):
```json
{
  "result": [
    {
      "data": [...],
      "colnames": ["region", "sales"],
      "coltypes": [1, 2]
    }
  ]
}
```

#### Create Chart

**Endpoint**: `POST /api/v1/chart/`

#### Update Chart

**Endpoint**: `PUT /api/v1/chart/{id}`

#### Delete Chart

**Endpoint**: `DELETE /api/v1/chart/{id}`

### Datasets

#### List All Datasets

**Endpoint**: `GET /api/v1/dataset/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/dataset/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "count": 20,
  "result": [
    {
      "id": 1,
      "table_name": "sales_data",
      "schema": "public",
      "database": {
        "id": 1,
        "database_name": "PostgreSQL"
      },
      "owners": [...],
      "columns": [...]
    }
  ]
}
```

#### Get Dataset Detail

**Endpoint**: `GET /api/v1/dataset/{id}`

#### Create Dataset

**Endpoint**: `POST /api/v1/dataset/`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/dataset/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "new_table",
    "schema": "public",
    "database": 1
  }'
```

#### Update Dataset

**Endpoint**: `PUT /api/v1/dataset/{id}`

#### Delete Dataset

**Endpoint**: `DELETE /api/v1/dataset/{id}`

### Databases

#### List All Database Connections

**Endpoint**: `GET /api/v1/database/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/database/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "count": 3,
  "result": [
    {
      "id": 1,
      "database_name": "PostgreSQL Production",
      "sqlalchemy_uri": "postgresql://***:***@host:5432/db",
      "expose_in_sqllab": true,
      "allow_run_async": true,
      "allow_ctas": true,
      "allow_cvas": true
    }
  ]
}
```

#### Get Database Detail

**Endpoint**: `GET /api/v1/database/{id}`

#### Create Database Connection

**Endpoint**: `POST /api/v1/database/`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/database/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "database_name": "New PostgreSQL",
    "sqlalchemy_uri": "postgresql://user:pass@host:5432/dbname",
    "expose_in_sqllab": true,
    "allow_ctas": true,
    "allow_cvas": true,
    "allow_dml": false
  }'
```

#### Update Database

**Endpoint**: `PUT /api/v1/database/{id}`

#### Delete Database

**Endpoint**: `DELETE /api/v1/database/{id}`

#### Test Database Connection

**Endpoint**: `POST /api/v1/database/test_connection/`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/database/test_connection/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sqlalchemy_uri": "postgresql://user:pass@host:5432/dbname"
  }'
```

### SQL Lab

#### Execute SQL Query

**Endpoint**: `POST /api/v1/sqllab/execute/`

**Request**:
```bash
curl -X POST "http://localhost:8088/api/v1/sqllab/execute/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "database_id": 1,
    "sql": "SELECT * FROM sales_data LIMIT 10",
    "schema": "public"
  }'
```

#### Get Query Results

**Endpoint**: `GET /api/v1/sqllab/results/{key}`

#### Get Saved Queries

**Endpoint**: `GET /api/v1/saved_query/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/saved_query/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Security & Permissions

#### Get Current User Info

**Endpoint**: `GET /api/v1/me/`

**Request**:
```bash
curl -X GET "http://localhost:8088/api/v1/me/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "result": {
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "email": "admin@example.com",
    "roles": ["Admin"],
    "permissions": [...]
  }
}
```

#### List Roles

**Endpoint**: `GET /api/v1/security/roles/`

#### List Users

**Endpoint**: `GET /api/v1/security/users/`

## Query Parameters

### Filtering

Gunakan `q` parameter untuk filtering:

```bash
# Filter dashboards by title
curl -X GET "http://localhost:8088/api/v1/dashboard/?q=(filters:!((col:dashboard_title,opr:ct,value:Sales)))" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Filter operators:
- `eq`: equals
- `neq`: not equals
- `gt`: greater than
- `lt`: less than
- `ct`: contains
- `sw`: starts with
- `ew`: ends with

### Sorting

```bash
# Sort by dashboard title ascending
curl -X GET "http://localhost:8088/api/v1/dashboard/?q=(order_column:dashboard_title,order_direction:asc)" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Pagination

```bash
# Get page 2 with 20 items per page
curl -X GET "http://localhost:8088/api/v1/dashboard/?q=(page:1,page_size:20)" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Selecting Fields

```bash
# Only get specific fields
curl -X GET "http://localhost:8088/api/v1/dashboard/?q=(columns:!(id,dashboard_title,published))" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Python Example

### Basic Usage

```python
import requests
from typing import Optional, Dict, Any

class SupersetAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self) -> bool:
        """Login and get access token"""
        url = f"{self.base_url}/api/v1/security/login"
        payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db",
            "refresh": True
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data.get('refresh_token')

            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.access_token:
            raise Exception("Not authenticated. Call login() first.")

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_dashboards(self) -> list:
        """Get all dashboards"""
        url = f"{self.base_url}/api/v1/dashboard/"

        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()['result']

    def get_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Get dashboard detail"""
        url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}"

        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()['result']

    def create_dashboard(self, title: str, published: bool = False) -> Dict[str, Any]:
        """Create new dashboard"""
        url = f"{self.base_url}/api/v1/dashboard/"
        payload = {
            "dashboard_title": title,
            "published": published
        }

        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()

        return response.json()['result']

    def update_dashboard(self, dashboard_id: int, **kwargs) -> Dict[str, Any]:
        """Update dashboard"""
        url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}"

        response = requests.put(url, headers=self._get_headers(), json=kwargs)
        response.raise_for_status()

        return response.json()['result']

    def delete_dashboard(self, dashboard_id: int) -> bool:
        """Delete dashboard"""
        url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}"

        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()

        return True

    def get_charts(self) -> list:
        """Get all charts"""
        url = f"{self.base_url}/api/v1/chart/"

        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()['result']

    def get_chart_data(self, chart_id: int) -> Dict[str, Any]:
        """Get chart data"""
        url = f"{self.base_url}/api/v1/chart/{chart_id}/data/"

        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()['result']

# Usage
api = SupersetAPI(
    base_url="http://localhost:8088",
    username="admin",
    password="admin"
)

# Login
if api.login():
    # Get all dashboards
    dashboards = api.get_dashboards()
    print(f"Found {len(dashboards)} dashboards")

    # Get dashboard detail
    dashboard = api.get_dashboard(1)
    print(f"Dashboard: {dashboard['dashboard_title']}")

    # Create new dashboard
    new_dashboard = api.create_dashboard("My New Dashboard")
    print(f"Created dashboard with ID: {new_dashboard['id']}")

    # Update dashboard
    api.update_dashboard(new_dashboard['id'], published=True)
    print("Dashboard published")
```

## Error Handling

### Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `204 No Content`: Success (for DELETE)
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Invalid/expired token
- `403 Forbidden`: No permission
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "message": "Error description",
  "errors": [
    {
      "message": "Detailed error message",
      "error_type": "ERROR_TYPE",
      "level": "error",
      "extra": {}
    }
  ]
}
```

### Example Error Handling

```python
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        # Token expired, refresh and retry
        print("Token expired, refreshing...")
        self.login()
        # Retry request

    elif e.response.status_code == 403:
        print("Permission denied")

    elif e.response.status_code == 404:
        print("Resource not found")

    else:
        print(f"HTTP Error: {e}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## Rate Limiting

Superset tidak memiliki built-in rate limiting, tapi best practice:

- Avoid excessive requests
- Implement client-side caching
- Use batch operations when possible
- Consider implementing rate limiting di reverse proxy (nginx, etc.)

## Next Steps

- [Authentication & Tokens →](./03-authentication-tokens.md)
- [Dashboard Permissions →](./04-dashboard-permissions.md)
- [Django Integration →](./05-django-integration.md)
