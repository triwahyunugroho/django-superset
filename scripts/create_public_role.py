"""
Script to create Public role in Superset and grant dashboard permissions
Run this inside the Superset container: docker compose exec superset python /app/scripts/create_public_role.py
"""
from superset.app import create_app
from superset import db

# Initialize the app
app = create_app()

# Initialize the app context
with app.app_context():
    security_manager = app.appbuilder.sm

    print("=" * 60)
    print("Creating/Updating Public Role in Superset")
    print("=" * 60)

    # Check if Public role exists
    public_role = security_manager.find_role("Public")

    if not public_role:
        print("\n[1/4] Creating Public role...")
        public_role = security_manager.add_role("Public")
        print("✓ Public role created")
    else:
        print("\n[1/4] Public role already exists")

    # Add permissions to Public role
    print("\n[2/4] Adding permissions to Public role...")

    # Permissions needed for viewing dashboards without login
    permissions_to_add = [
        ("can_read", "Dashboard"),
        ("can_read", "Chart"),
        ("can_read", "Dataset"),
        ("can_read", "Database"),
        ("can_read", "Query"),
        ("can_explore", "Superset"),
        ("can_dashboard", "Superset"),
        ("can_explore_json", "Superset"),
        ("can_slice", "Superset"),
        ("can_this_form_get", "DashboardModelView"),
        ("can_this_form_post", "DashboardModelView"),
        ("menu_access", "Dashboard"),
        ("menu_access", "Dashboards"),
    ]

    added_count = 0
    for permission_name, view_name in permissions_to_add:
        # Find or create permission
        perm_view = security_manager.find_permission_view_menu(permission_name, view_name)

        if perm_view:
            # Check if permission already in role
            if perm_view not in public_role.permissions:
                public_role.permissions.append(perm_view)
                added_count += 1
                print(f"  + Added: {permission_name} on {view_name}")
        else:
            # Try to create the permission
            try:
                perm_view = security_manager.add_permission_view_menu(permission_name, view_name)
                if perm_view:
                    public_role.permissions.append(perm_view)
                    added_count += 1
                    print(f"  + Created and added: {permission_name} on {view_name}")
            except Exception as e:
                print(f"  - Could not add {permission_name} on {view_name}: {e}")

    if added_count > 0:
        db.session.commit()
        print(f"\n✓ Added {added_count} permissions to Public role")
    else:
        print("\n✓ All permissions already present")

    # Update Superset config to use Public role
    print("\n[3/4] Configuring AUTH_ROLE_PUBLIC...")
    if hasattr(app.config, 'AUTH_ROLE_PUBLIC'):
        print(f"✓ AUTH_ROLE_PUBLIC is set to: {app.config.get('AUTH_ROLE_PUBLIC')}")
    else:
        print("⚠ AUTH_ROLE_PUBLIC not set in config")

    # List all dashboards
    print("\n[4/4] Available dashboards:")
    from superset.models.dashboard import Dashboard
    dashboards = db.session.query(Dashboard).all()

    if dashboards:
        for dashboard in dashboards:
            print(f"  - ID: {dashboard.id}, Title: {dashboard.dashboard_title}")
            print(f"    URL: http://localhost:8088/superset/dashboard/{dashboard.id}/")
            print(f"    Standalone: http://localhost:8088/superset/dashboard/{dashboard.id}/?standalone=true")

            # Add Public role to dashboard roles
            if public_role not in dashboard.roles:
                dashboard.roles.append(public_role)
                print(f"    ✓ Added Public role to this dashboard")
            else:
                print(f"    ✓ Public role already assigned")

        db.session.commit()
    else:
        print("  No dashboards found. Please create a dashboard first.")

    print("\n" + "=" * 60)
    print("Configuration Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Superset container: docker compose restart superset")
    print("2. Open http://localhost:8000/dashboard/ to view embedded dashboard")
    print("3. Dashboard should now be accessible without login")
    print("")
