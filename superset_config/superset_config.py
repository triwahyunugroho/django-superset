"""
Superset configuration for Django integration.
"""

import os

# Flask App Secret Key
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your_secret_key_here')

# Database URI
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'SUPERSET_DATABASE_URI',
    'postgresql+psycopg2://superset:superset@postgres:5432/superset'
)

# Redis configuration for caching and Celery
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
}

# Data cache configuration
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 2,
}

# Celery configuration for async queries
class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    worker_prefetch_multiplier = 1
    task_acks_late = True

CELERY_CONFIG = CeleryConfig

# Feature flags
FEATURE_FLAGS = {
    # Enable Dashboard RBAC (Role-Based Access Control)
    'DASHBOARD_RBAC': True,

    # Enable embedding dashboards
    'EMBEDDED_SUPERSET': True,

    # Enable native dashboard filters
    'DASHBOARD_NATIVE_FILTERS': True,

    # Enable async queries
    'GLOBAL_ASYNC_QUERIES': True,

    # Enable template processing
    'ENABLE_TEMPLATE_PROCESSING': True,

    # Other useful features
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_FILTERS_EXPERIMENTAL': True,
    'ALLOW_FULL_CSV_EXPORT': True,
}

# Guest token configuration for embedding
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = os.environ.get(
    'GUEST_TOKEN_JWT_SECRET',
    'change-this-guest-token-secret-key'
)
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# CORS configuration to allow embedding
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
        '*',  # Allow all origins for development (restrict in production!)
    ]
}

# Public role configuration
# Set to None to prevent anonymous access by default
PUBLIC_ROLE_LIKE = None

# If you want to enable anonymous access with specific permissions:
# PUBLIC_ROLE_LIKE = "Gamma"

# Security configuration
TALISMAN_ENABLED = False  # Disable in development
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = ['superset.views.core.log']

# Session configuration
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# Upload folder
UPLOAD_FOLDER = '/app/superset_home/uploads/'

# Image upload configuration
UPLOAD_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

# Languages
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'id': {'flag': 'id', 'name': 'Indonesia'},
}

# Default language
BABEL_DEFAULT_LOCALE = 'id'

# Logging configuration
LOG_LEVEL = 'INFO'

# Allow embedding in iframes
HTTP_HEADERS = {'X-Frame-Options': 'ALLOWALL'}

# WebDriver configuration (for thumbnails and alerts)
WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--force-device-scale-factor=2.0",
    "--high-dpi-support=2.0",
    "--headless",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-extensions",
]

# CSV export configuration
CSV_EXPORT = {
    'encoding': 'utf-8',
}

# SQL Lab configuration
SQLLAB_ASYNC_TIME_LIMIT_SEC = 300  # 5 minutes
SQLLAB_TIMEOUT = 300  # 5 minutes

# Results backend configuration
RESULTS_BACKEND = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 3,
}

# Thumbnail cache configuration
THUMBNAIL_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 4,
}
