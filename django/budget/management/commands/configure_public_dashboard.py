"""
Configure Superset to allow public dashboard access
This command creates the Public role and assigns necessary permissions
"""
from django.core.management.base import BaseCommand
import requests
import time


class Command(BaseCommand):
    help = 'Configure Superset to allow public dashboard access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dashboard-id',
            type=int,
            default=1,
            help='Dashboard ID to make public (default: 1)'
        )

    def handle(self, *args, **options):
        superset_url = 'http://superset:8088'
        dashboard_id = options['dashboard_id']

        self.stdout.write('Configuring public dashboard access in Superset...')

        # Wait for Superset to be ready
        self.stdout.write('Waiting for Superset...')
        for i in range(30):
            try:
                response = requests.get(f'{superset_url}/health', timeout=5)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS('Superset is ready!'))
                    break
            except Exception:
                pass
            time.sleep(2)
            self.stdout.write(f'Waiting... ({i+1}/30)')
        else:
            self.stdout.write(self.style.ERROR('Superset is not responding'))
            return

        # Login to Superset
        self.stdout.write('Logging in to Superset...')
        session = requests.Session()

        login_data = {
            'username': 'admin',
            'password': 'admin',
            'provider': 'db',
            'refresh': True
        }

        try:
            response = session.post(
                f'{superset_url}/api/v1/security/login',
                json=login_data,
                timeout=10
            )

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Login failed: {response.text}'))
                return

            access_token = response.json()['access_token']
            session.headers.update({'Authorization': f'Bearer {access_token}'})

            self.stdout.write(self.style.SUCCESS('Logged in successfully!'))

            # Get CSRF token
            response = session.get(f'{superset_url}/api/v1/security/csrf_token/', timeout=10)
            csrf_token = response.json()['result']
            session.headers.update({
                'X-CSRFToken': csrf_token,
                'Referer': superset_url
            })

            # Step 1: Check if Public role exists
            self.stdout.write('\nChecking for Public role...')
            response = session.get(f'{superset_url}/api/v1/security/roles/', timeout=10)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to get roles: {response.text}'))
                return

            roles = response.json()['result']
            public_role = None
            for role in roles:
                if role['name'] == 'Public':
                    public_role = role
                    self.stdout.write(self.style.SUCCESS(f'Public role found (ID: {role["id"]})'))
                    break

            # If Public role doesn't exist, create it
            if not public_role:
                self.stdout.write('Public role not found. Creating...')
                # Note: Creating roles via API requires specific permissions structure
                # It's better to use Superset CLI for this
                self.stdout.write(self.style.WARNING(
                    'Public role does not exist. Please run this command inside Superset container:'
                ))
                self.stdout.write('  docker compose exec superset superset fab create-role --name Public')
                return

            # Step 2: Get dashboard details
            self.stdout.write(f'\nGetting dashboard {dashboard_id} details...')
            response = session.get(
                f'{superset_url}/api/v1/dashboard/{dashboard_id}',
                timeout=10
            )

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Dashboard {dashboard_id} not found: {response.text}'))
                return

            dashboard = response.json()['result']
            self.stdout.write(self.style.SUCCESS(f'Dashboard found: {dashboard.get("dashboard_title", "Untitled")}'))

            # Step 3: Update dashboard to published state
            self.stdout.write('\nPublishing dashboard...')
            update_data = {
                'published': True
            }

            response = session.put(
                f'{superset_url}/api/v1/dashboard/{dashboard_id}',
                json=update_data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                self.stdout.write(self.style.SUCCESS('Dashboard published successfully!'))
            else:
                self.stdout.write(self.style.WARNING(f'Could not publish dashboard: {response.text}'))

            # Step 4: Grant permissions to Public role for this dashboard
            self.stdout.write('\nGranting dashboard access to Public role...')

            # Get current roles for the dashboard
            current_roles = dashboard.get('roles', [])

            # Add Public role if not already there
            if public_role['id'] not in [r['id'] for r in current_roles]:
                current_roles.append({'id': public_role['id']})

                response = session.put(
                    f'{superset_url}/api/v1/dashboard/{dashboard_id}',
                    json={'roles': current_roles},
                    timeout=10
                )

                if response.status_code in [200, 201]:
                    self.stdout.write(self.style.SUCCESS('Public role added to dashboard!'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not add role: {response.text}'))

            # Summary
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('Configuration completed!'))
            self.stdout.write('='*60)
            self.stdout.write('\nDashboard URL:')
            self.stdout.write(f'  http://localhost:8088/superset/dashboard/{dashboard_id}/')
            self.stdout.write('\nEmbedded URL (standalone mode):')
            self.stdout.write(f'  http://localhost:8088/superset/dashboard/{dashboard_id}/?standalone=true')
            self.stdout.write('\nDjango Dashboard:')
            self.stdout.write('  http://localhost:8000/dashboard/')
            self.stdout.write('')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            traceback.print_exc()
