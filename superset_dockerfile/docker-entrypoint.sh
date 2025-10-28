#!/bin/bash
set -e

echo "🚀 Starting Superset initialization..."

# Wait a bit for database to be fully ready
sleep 5

# Initialize Superset database
echo "📊 Upgrading Superset database..."
superset db upgrade

# Check if admin user exists by trying to create it
echo "🔍 Checking if admin user exists..."
CREATE_OUTPUT=$(superset fab create-admin \
    --username "${SUPERSET_ADMIN_USER:-admin}" \
    --firstname "${SUPERSET_ADMIN_FIRSTNAME:-Admin}" \
    --lastname "${SUPERSET_ADMIN_LASTNAME:-User}" \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@example.com}" \
    --password "${SUPERSET_ADMIN_PASSWORD:-admin}" 2>&1 || true)

if echo "$CREATE_OUTPUT" | grep -q "User already exists"; then
    echo "✅ Admin user already exists. Skipping creation."
else
    echo "✅ Admin user created successfully!"
fi

# Initialize Superset (roles, permissions, etc.)
echo "🔐 Initializing Superset roles and permissions..."
superset init

echo "✨ Superset initialization complete!"
echo "🌐 Starting Superset web server..."

# Start Superset server
exec superset run -h 0.0.0.0 -p 8088 --with-threads --reload --debugger
