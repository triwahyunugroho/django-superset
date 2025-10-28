# Parameters & Filtering Guide

Panduan lengkap untuk menggunakan parameters dan filtering di Superset + Django integration.

## Table of Contents

1. [Overview](#overview)
2. [Dashboard Native Filters](#dashboard-native-filters)
3. [Jinja Templates in SQL](#jinja-templates-in-sql)
4. [Row Level Security (RLS)](#row-level-security-rls)
5. [URL Parameters](#url-parameters)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

## Overview

Project ini support 4 metode filtering yang bisa dikombinasikan:

| Method | Level | Use Case | Requires Code |
|--------|-------|----------|--------------|
| **Dashboard Native Filters** | UI | User-interactive filtering | No |
| **Jinja Templates** | Query | Dynamic SQL based on filters | SQL only |
| **Row Level Security (RLS)** | Backend | Per-user data restrictions | Python |
| **URL Parameters** | Django | Pass filters from URL | Python |

### Feature Flags Already Enabled

Configuration di `superset_config/superset_config.py`:

```python
FEATURE_FLAGS = {
    'DASHBOARD_NATIVE_FILTERS': True,        # UI filters
    'DASHBOARD_CROSS_FILTERS': True,         # Click chart to filter
    'DASHBOARD_FILTERS_EXPERIMENTAL': True,  # Advanced filters
    'ENABLE_TEMPLATE_PROCESSING': True,      # Jinja templates
    'DASHBOARD_RBAC': True,                  # Role-based access
    'EMBEDDED_SUPERSET': True,               # Embedding support
}
```

## Dashboard Native Filters

### What Are Native Filters?

UI-based filters yang user bisa control tanpa edit code. Filters apply ke semua charts di dashboard.

### Creating Native Filters

1. **Open Dashboard** di Superset
2. **Click "⚙️"** (Settings) di kanan atas
3. **Click "🔽"** dropdown > **"Add/Edit filters"**
4. **Click "+ Add filter"**
5. **Configure filter**:
   - **Name**: Filter name (e.g., "OPD Filter")
   - **Dataset**: Pilih dataset
   - **Column**: Pilih kolom untuk filter (e.g., `opd_nama`)
   - **Type**: Dropdown, Select, Range, Time, etc.
   - **Default value**: Optional
6. **Apply to charts**: Pilih charts yang akan di-filter
7. **Save**

### Filter Types

#### 1. Select/Dropdown Filter

Pilih satu atau multiple values dari list.

**Best for**: Categorical data (OPD, kategori belanja, program)

**Configuration**:
```
Type: Value
Control type: Select filter
Multiple: Yes/No
Search: Yes (for long lists)
```

**Example**: Filter by OPD
- Column: `opd_nama`
- Multiple: Yes
- Users can select "Dinas Pendidikan", "Dinas Kesehatan", etc.

#### 2. Time Range Filter

Pilih date/time range.

**Best for**: Date columns, time series data

**Configuration**:
```
Type: Time range
Column: your_date_column
Default: Last 90 days / This year / Custom
```

**Example**: Filter by periode
- Column: `created_at` or `tahun`
- Default: This year

#### 3. Numerical Range Filter

Slider untuk range numerik.

**Best for**: Numerical data (amount, percentage, count)

**Configuration**:
```
Type: Numerical range
Column: nilai_anggaran
Min/Max: Auto or custom
```

**Example**: Filter by budget amount
- Column: `nilai_rencana`
- Range: 0 - 10,000,000,000

#### 4. Text Search Filter

Free text search.

**Best for**: Searching in text columns

**Configuration**:
```
Type: Value
Control type: Search
```

### Cross Filters

**What**: Click pada chart untuk filter charts lainnya.

**Example**: Click bar "Dinas Pendidikan" di Bar Chart → semua charts akan filter untuk show hanya data Dinas Pendidikan.

**How to enable**:
1. Edit dashboard
2. Click chart settings
3. Enable "Emit dashboard cross filters"

## Jinja Templates in SQL

### What Are Jinja Templates?

Dynamic SQL queries menggunakan Jinja2 syntax. Query berubah berdasarkan filter values.

### Basic Syntax

```sql
-- Check if filter has value
{% if filter_values('filter_name') %}
    -- SQL code here
{% endif %}

-- Get filter value
{{ filter_values('filter_name')[0] }}

-- Use in WHERE clause
WHERE column IN {{ filter_values('filter_name')|where_in }}
```

### Available Jinja Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `filter_values('name')` | Get filter values | `['Dinas Pendidikan', 'Dinas Kesehatan']` |
| `from_dttm` | Start datetime from time filter | `2024-01-01 00:00:00` |
| `to_dttm` | End datetime from time filter | `2024-12-31 23:59:59` |
| `get_filters('column')` | Get filters for specific column | Similar to filter_values |

### Examples

#### Example 1: Optional OPD Filter

```sql
SELECT
    opd_nama,
    program_nama,
    SUM(nilai_rencana) as total_rencana,
    SUM(nilai_realisasi) as total_realisasi
FROM v_summary_anggaran
WHERE tahun = 2024
{% if filter_values('opd_filter') %}
    AND opd_nama IN {{ filter_values('opd_filter')|where_in }}
{% endif %}
GROUP BY opd_nama, program_nama
ORDER BY total_rencana DESC
```

**Behavior**:
- No filter selected → Query returns all OPDs
- "Dinas Pendidikan" selected → Query filters to only Dinas Pendidikan

#### Example 2: Multiple Filters

```sql
SELECT
    opd_nama,
    kategori_belanja,
    tahun,
    triwulan,
    SUM(nilai_rencana) as rencana,
    SUM(nilai_realisasi) as realisasi,
    ROUND((SUM(nilai_realisasi)::numeric / NULLIF(SUM(nilai_rencana), 0)) * 100, 2) as persentase
FROM v_summary_anggaran
WHERE 1=1
{% if filter_values('opd_filter') %}
    AND opd_nama IN {{ filter_values('opd_filter')|where_in }}
{% endif %}
{% if filter_values('kategori_filter') %}
    AND kategori_belanja IN {{ filter_values('kategori_filter')|where_in }}
{% endif %}
{% if filter_values('tahun_filter') %}
    AND tahun = {{ filter_values('tahun_filter')[0] }}
{% endif %}
{% if filter_values('triwulan_filter') %}
    AND triwulan IN {{ filter_values('triwulan_filter')|where_in }}
{% endif %}
GROUP BY opd_nama, kategori_belanja, tahun, triwulan
ORDER BY tahun DESC, triwulan, opd_nama
```

#### Example 3: Time Range Filter

```sql
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_transactions,
    SUM(amount) as total_amount
FROM transactions
WHERE 1=1
{% if from_dttm %}
    AND created_at >= '{{ from_dttm }}'
{% endif %}
{% if to_dttm %}
    AND created_at <= '{{ to_dttm }}'
{% endif %}
GROUP BY month
ORDER BY month
```

#### Example 4: Conditional Aggregation

```sql
SELECT
    opd_nama,
    {% if filter_values('metric_filter') %}
        {% if filter_values('metric_filter')[0] == 'rencana' %}
            SUM(nilai_rencana) as value
        {% elif filter_values('metric_filter')[0] == 'realisasi' %}
            SUM(nilai_realisasi) as value
        {% else %}
            ROUND((SUM(nilai_realisasi)::numeric / NULLIF(SUM(nilai_rencana), 0)) * 100, 2) as value
        {% endif %}
    {% else %}
        SUM(nilai_rencana) as value
    {% endif %}
FROM v_summary_anggaran
GROUP BY opd_nama
ORDER BY value DESC
```

### Testing Jinja Templates

1. **SQL Lab** → Write query with Jinja
2. **Click "▶ Run"** → See compiled SQL in logs
3. **Add to Dashboard** with filters
4. **Test filter interactions**

## Row Level Security (RLS)

### What is RLS?

Backend-enforced data filtering per-user. Django menentukan data apa yang user boleh lihat.

### How It Works

```
User Request → Django → Generate Guest Token with RLS → Superset applies RLS to all queries
```

### Implementation in Django

#### Basic RLS

```python
from services.superset_service import SupersetService

superset = SupersetService()

# User hanya bisa lihat data satu OPD
rls_rules = [{
    "clause": "opd_nama = 'Dinas Pendidikan'"
}]

guest_token = superset.create_guest_token(
    dashboard_uuid=dashboard_uuid,
    user_info={
        "username": "kepala_diknas",
        "first_name": "Kepala",
        "last_name": "Diknas"
    },
    rls_rules=rls_rules
)
```

#### Multiple Conditions

```python
# User bisa lihat beberapa OPD
rls_rules = [{
    "clause": "opd_nama IN ('Dinas Pendidikan', 'Dinas Kesehatan')"
}]
```

#### Complex Rules

```python
# Kombinasi multiple conditions
rls_rules = [{
    "clause": "opd_nama = 'Dinas Pendidikan' AND tahun >= 2023"
}]
```

#### Multiple RLS Rules

```python
# Each rule applies to different datasets
rls_rules = [
    {
        "clause": "opd_nama = 'Dinas Pendidikan'"
    },
    {
        "clause": "region = 'Jakarta'"
    }
]
```

### RLS Based on User Role

```python
def get_rls_for_user(user):
    """Generate RLS rules based on user role"""

    if user.is_superuser:
        # Admin: no restrictions
        return None

    elif user.role == 'kepala_dinas':
        # Kepala Dinas: only their OPD
        return [{
            "clause": f"opd_nama = '{user.profile.opd_nama}'"
        }]

    elif user.role == 'dprd':
        # DPRD: all OPDs but only recent years
        return [{
            "clause": "tahun >= 2023"
        }]

    elif user.role == 'public':
        # Public: only published data
        return [{
            "clause": "is_public = true"
        }]

    else:
        # Default: no access
        return [{
            "clause": "1 = 0"  # No data
        }]
```

### Using RLS in Views

```python
# dashboards/views.py

from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view_with_rls(request, dashboard_uuid):
    """Dashboard with user-specific RLS"""

    superset = SupersetService()

    # Generate RLS based on user
    rls_rules = get_rls_for_user(request.user)

    # Create guest token with RLS
    guest_token = superset.create_guest_token(
        dashboard_uuid=dashboard_uuid,
        user_info={
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name
        },
        rls_rules=rls_rules
    )

    context = {
        'dashboard_uuid': dashboard_uuid,
        'guest_token': guest_token,
    }

    return render(request, 'dashboards/dashboard_view.html', context)
```

## URL Parameters

### Passing Parameters via URL

```python
# URL: /dashboards/xxx/?opd=Dinas+Pendidikan&tahun=2024

def dashboard_view_with_params(request, dashboard_uuid):
    """Dashboard with URL parameters converted to RLS"""

    # Get parameters from URL
    opd = request.GET.get('opd')
    tahun = request.GET.get('tahun')

    # Build RLS rules from parameters
    rls_rules = []

    if opd:
        rls_rules.append({
            "clause": f"opd_nama = '{opd}'"
        })

    if tahun:
        rls_rules.append({
            "clause": f"tahun = {tahun}"
        })

    # Create guest token with RLS
    superset = SupersetService()
    guest_token = superset.create_guest_token(
        dashboard_uuid=dashboard_uuid,
        user_info={"username": "guest", "first_name": "Guest", "last_name": "User"},
        rls_rules=rls_rules if rls_rules else None
    )

    # ... render template
```

### Security Considerations

**⚠️ IMPORTANT**: Always sanitize URL parameters to prevent SQL injection!

```python
import re

def sanitize_param(value, allowed_pattern=r'^[a-zA-Z0-9\s]+$'):
    """Sanitize URL parameter"""
    if not re.match(allowed_pattern, value):
        raise ValueError("Invalid parameter value")
    return value

# Usage
opd = sanitize_param(request.GET.get('opd', ''))
tahun = int(request.GET.get('tahun', 0))  # Convert to int
```

## Best Practices

### 1. Choose the Right Method

| Scenario | Recommended Method |
|----------|-------------------|
| User wants to filter interactively | Dashboard Native Filters |
| Query needs to adapt to filters | Jinja Templates |
| Different data per user role | Row Level Security (RLS) |
| Deep links with pre-set filters | URL Parameters |

### 2. Combine Methods

You can use multiple methods together:

```
Native Filters (UI)
    → Jinja Templates (Dynamic SQL)
        → RLS (Backend restrictions)
```

**Example**: Dashboard dengan:
- **RLS**: User hanya lihat OPD mereka
- **Native Filters**: User bisa filter by tahun, triwulan
- **Jinja**: Query adjust berdasarkan filters

### 3. Performance Tips

1. **Use WHERE clause filtering** (fast) over HAVING clause (slow)
2. **Index filtered columns** in database
3. **Cache guest tokens** (5 minutes default)
4. **Limit filter options** (don't show 10000 options in dropdown)

### 4. Security Tips

1. **Always use RLS** for sensitive data
2. **Validate URL parameters** before using in RLS
3. **Use parameterized queries** to prevent SQL injection
4. **Test RLS rules** thoroughly for each user role

### 5. User Experience Tips

1. **Provide default values** for filters (e.g., current year)
2. **Use meaningful filter names** ("Pilih OPD" not "Filter 1")
3. **Group related filters** together
4. **Add descriptions** to complex filters

## Examples

### Example 1: Public Dashboard with Optional Filters

**Use Case**: Public budget dashboard, user can optionally filter by OPD

**Setup**:
1. Create dashboard with charts
2. Add native filters for OPD, tahun
3. Use Jinja templates in queries
4. No RLS (public data)

**SQL Query**:
```sql
SELECT
    opd_nama,
    SUM(nilai_rencana) as rencana,
    SUM(nilai_realisasi) as realisasi
FROM v_summary_anggaran
WHERE tahun = 2024
{% if filter_values('opd_filter') %}
    AND opd_nama IN {{ filter_values('opd_filter')|where_in }}
{% endif %}
GROUP BY opd_nama
```

**Django View**:
```python
def public_dashboard(request, dashboard_uuid):
    superset = SupersetService()

    # No RLS, public data
    guest_token = superset.create_guest_token(
        dashboard_uuid=dashboard_uuid,
        user_info={"username": "public", "first_name": "Public", "last_name": "User"},
        rls_rules=None
    )

    # ... render
```

### Example 2: Role-Based Dashboard

**Use Case**: Kepala Dinas hanya lihat data dinasnya, DPRD lihat semua

**Setup**:
1. Create dashboard
2. Add native filters (optional)
3. Django generates RLS based on user role

**Django View**:
```python
@login_required
def role_based_dashboard(request, dashboard_uuid):
    superset = SupersetService()
    user = request.user

    # Generate RLS based on role
    if user.role == 'kepala_dinas':
        rls_rules = [{
            "clause": f"opd_nama = '{user.profile.opd_nama}'"
        }]
    elif user.role == 'dprd':
        rls_rules = None  # Can see all
    else:
        rls_rules = [{"clause": "1 = 0"}]  # No access

    guest_token = superset.create_guest_token(
        dashboard_uuid=dashboard_uuid,
        user_info={
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        },
        rls_rules=rls_rules
    )

    # ... render
```

### Example 3: Dashboard with URL Parameters

**Use Case**: Email notification dengan deep link ke specific OPD

**URL**: `/dashboards/xxx/?opd=Dinas+Pendidikan&highlight=true`

**Django View**:
```python
def dashboard_with_deeplink(request, dashboard_uuid):
    superset = SupersetService()

    # Get parameters
    opd = request.GET.get('opd')
    highlight = request.GET.get('highlight') == 'true'

    # Apply RLS if OPD specified
    rls_rules = None
    if opd:
        # Sanitize!
        opd_clean = sanitize_param(opd)
        rls_rules = [{
            "clause": f"opd_nama = '{opd_clean}'"
        }]

    guest_token = superset.create_guest_token(
        dashboard_uuid=dashboard_uuid,
        user_info={"username": "guest", "first_name": "Guest", "last_name": "User"},
        rls_rules=rls_rules
    )

    context = {
        'dashboard_uuid': dashboard_uuid,
        'guest_token': guest_token,
        'highlight_mode': highlight,
        'filtered_opd': opd,
    }

    return render(request, 'dashboards/dashboard_view.html', context)
```

## Testing

### Test Native Filters

1. Open dashboard di Superset
2. Add test filters
3. Change filter values
4. Verify charts update correctly

### Test Jinja Templates

```python
# Django shell
docker exec django-app python manage.py shell

from services.superset_service import SupersetService
s = SupersetService()

# Get dashboard and check if queries work
info = s.get_dashboard_visibility_info('your-uuid')
print(info)
```

### Test RLS

```python
# Test RLS with different rules
rls_test_cases = [
    None,  # No restrictions
    [{"clause": "opd_nama = 'Dinas Pendidikan'"}],  # Single OPD
    [{"clause": "tahun >= 2023"}],  # Recent years
    [{"clause": "1 = 0"}],  # No access
]

for rls in rls_test_cases:
    token = s.create_guest_token(
        dashboard_uuid='xxx',
        user_info={"username": "test", "first_name": "Test", "last_name": "User"},
        rls_rules=rls
    )
    print(f"RLS: {rls}")
    print(f"Token created: {len(token)} chars\n")
```

## Troubleshooting

### Jinja Template Errors

**Error**: `Jinja template error`

**Solution**: Check syntax, use SQL Lab to test

### Filters Not Working

**Error**: Charts don't update when filter changes

**Solution**:
1. Check chart is linked to filter
2. Verify column names match
3. Check Jinja syntax in query

### RLS Not Applied

**Error**: User sees data they shouldn't

**Solution**:
1. Verify RLS rules in guest token
2. Check column names in RLS clause
3. Test RLS with SQL Lab

### Performance Issues

**Error**: Dashboard loads slowly with filters

**Solution**:
1. Add database indexes on filtered columns
2. Simplify queries
3. Reduce number of charts
4. Use result caching

---

**Next Steps**:
- Read [Troubleshooting Guide](08-troubleshooting-guide.md)
- Explore [Django Integration](05-django-integration.md)
- Check [Implementation Complete](06-implementation-complete.md)
