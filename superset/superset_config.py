import os
from datetime import timedelta

# Superset specific config
ROW_LIMIT = 5000

# Flask App Builder configuration
# Your App secret key will be used for securely signing the session cookie
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your_secret_key_change_this_in_production')

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ.get('DATABASE_USER', 'superset_user'),
    os.environ.get('DATABASE_PASSWORD', 'superset_password'),
    os.environ.get('DATABASE_HOST', 'postgres'),
    os.environ.get('DATABASE_PORT', '5432'),
    os.environ.get('DATABASE_DB', 'superset_db')
)

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []

# Disable WTF CSRF time limit for embedded dashboards
WTF_CSRF_TIME_LIMIT = None

# Allow embedding from any origin
WTF_CSRF_SSL_STRICT = False
WTF_CSRF_CHECK_DEFAULT = False

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY', '')

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': os.environ.get('REDIS_HOST', 'redis'),
    'CACHE_REDIS_PORT': os.environ.get('REDIS_PORT', 6379),
    'CACHE_REDIS_DB': 1,
}

# Celery configuration for async queries
class CeleryConfig:
    broker_url = 'redis://{}:{}/0'.format(
        os.environ.get('REDIS_HOST', 'redis'),
        os.environ.get('REDIS_PORT', 6379)
    )
    imports = ('superset.sql_lab', 'superset.tasks')
    result_backend = 'redis://{}:{}/0'.format(
        os.environ.get('REDIS_HOST', 'redis'),
        os.environ.get('REDIS_PORT', 6379)
    )
    worker_prefetch_multiplier = 1
    task_acks_late = False
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
    }

CELERY_CONFIG = CeleryConfig

# Enable CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']  # Allow all origins for development
}

# Override Flask-Talisman
OVERRIDE_HTTP_HEADERS = {
    'X-Frame-Options': None
}

# Enable proxy fix for proper header handling
ENABLE_PROXY_FIX = True

# Session cookie settings for iframe
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
SESSION_COOKIE_HTTPONLY = False

# Public role configuration - For guest tokens only, not for UI access
# Comment out AUTH_ROLE_PUBLIC to require login for Superset UI
# AUTH_ROLE_PUBLIC = 'Public'

# Note: We use guest tokens for embedded dashboards instead of public role
# This allows login to Superset UI while still supporting embedded access

# Enable embedding
FEATURE_FLAGS = {
    'EMBEDDED_SUPERSET': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_RBAC': False,
}

# Guest token configuration
GUEST_ROLE_NAME = 'Gamma'
GUEST_TOKEN_JWT_SECRET = os.environ.get('SUPERSET_SECRET_KEY', 'your_secret_key_change_this_in_production')
GUEST_TOKEN_JWT_ALGO = 'HS256'
GUEST_TOKEN_HEADER_NAME = 'X-GuestToken'
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# HTTP headers - Allow embedding in iframe
HTTP_HEADERS = {}

# Talisman security settings - disable X-Frame-Options
TALISMAN_ENABLED = False
TALISMAN_CONFIG = {
    'content_security_policy': None,
    'force_https': False,
}

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Localization
BABEL_DEFAULT_LOCALE = 'en'
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'id': {'flag': 'id', 'name': 'Indonesian'},
}
