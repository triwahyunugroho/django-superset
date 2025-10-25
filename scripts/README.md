# Superset Public Dashboard Configuration

This folder contains scripts to configure public access for Superset dashboards.

## Making a Dashboard Public

To make a Superset dashboard accessible without login (public access), run:

```bash
# Copy the script to the Superset container
docker compose cp scripts/create_public_role.py superset:/app/create_public_role.py

# Run the script inside Superset container
docker compose exec superset python /app/create_public_role.py

# Restart Superset to apply changes
docker compose restart superset
```

## What the script does:

1. **Creates/Updates Public Role**: Ensures the "Public" role exists in Superset
2. **Grants Permissions**: Adds necessary permissions to the Public role:
   - can_read on Dashboard, Chart, Dataset, Database, Query
   - can_explore, can_dashboard, can_explore_json, can_slice on Superset
   - menu_access for Dashboard and Dashboards
3. **Assigns Role to Dashboards**: Automatically adds the Public role to all existing dashboards
4. **Lists Available Dashboards**: Shows dashboard IDs and URLs

## Manual Configuration (Alternative)

If you prefer to configure manually through Superset UI:

1. Login to Superset: http://localhost:8088 (admin/admin)
2. Go to **Settings > List Roles**
3. Find or create the "Public" role
4. Add permissions:
   - can read on Dashboard
   - can read on Chart
   - can read on Dataset
5. Go to your dashboard
6. Click the **"..."** menu > **Share**
7. Under "Dashboard permissions", add the "Public" role

## Verifying Public Access

After configuration:

1. Open an incognito/private browser window
2. Navigate to: `http://localhost:8088/superset/dashboard/{dashboard_id}/?standalone=true`
3. Dashboard should load without requiring login

## Django Integration

The Django app at http://localhost:8000/dashboard/ embeds the Superset dashboard using an iframe. With public access configured, the dashboard will display automatically without authentication.

## Configuration Files

- `superset/superset_config.py`: Contains Superset configuration including:
  - `AUTH_ROLE_PUBLIC = 'Public'`
  - `FEATURE_FLAGS['EMBEDDED_SUPERSET'] = True`
  - CORS and X-Frame-Options settings for iframe embedding

## Troubleshooting

**Dashboard still requires login:**
- Run the script again to ensure Public role has correct permissions
- Check that `AUTH_ROLE_PUBLIC = 'Public'` is in `superset_config.py`
- Restart Superset: `docker compose restart superset`

**Iframe shows "Refused to display":**
- Verify `TALISMAN_ENABLED = False` in `superset_config.py`
- Check that `SESSION_COOKIE_SAMESITE = 'None'` is set
- Ensure CORS is enabled for all origins

**Script fails to run:**
- Ensure Superset container is running: `docker compose ps`
- Check Superset logs: `docker compose logs superset`
