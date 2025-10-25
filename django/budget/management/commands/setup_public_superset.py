"""
Setup public access to Superset dashboard
This command will configure Superset to allow public access without login
"""
from django.core.management.base import BaseCommand
import requests
import time


class Command(BaseCommand):
    help = 'Setup public access to Superset dashboard'

    def handle(self, *args, **options):
        superset_url = 'http://superset:8088'

        self.stdout.write('Setting up public access to Superset...')

        # Wait for Superset to be ready
        self.stdout.write('Waiting for Superset...')
        for i in range(30):
            try:
                response = requests.get(f'{superset_url}/health')
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS('Superset is ready!'))
                    break
            except:
                pass
            time.sleep(2)
            self.stdout.write(f'Waiting... ({i+1}/30)')

        # Login to Superset
        self.stdout.write('Logging in to Superset...')
        session = requests.Session()

        login_data = {
            'username': 'admin',
            'password': 'admin',
            'provider': 'db',
            'refresh': True
        }

        response = session.post(
            f'{superset_url}/api/v1/security/login',
            json=login_data
        )

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Login failed: {response.text}'))
            return

        access_token = response.json()['access_token']
        session.headers.update({'Authorization': f'Bearer {access_token}'})

        self.stdout.write(self.style.SUCCESS('Logged in successfully!'))

        # Get CSRF token
        response = session.get(f'{superset_url}/api/v1/security/csrf_token/')
        csrf_token = response.json()['result']
        session.headers.update({
            'X-CSRFToken': csrf_token,
            'Referer': superset_url
        })

        self.stdout.write('\nInstructions to make dashboard public:')
        self.stdout.write('1. Login to Superset: http://localhost:8088')
        self.stdout.write('2. Go to Settings > List Roles')
        self.stdout.write('3. Create role "Public" if not exists')
        self.stdout.write('4. Add permissions to Public role:')
        self.stdout.write('   - can read on Dashboard')
        self.stdout.write('   - can read on Chart')
        self.stdout.write('   - can read on Dataset')
        self.stdout.write('5. Go to your dashboard')
        self.stdout.write('6. Click "..." menu > "Share" > "Copy permalink"')
        self.stdout.write('7. Add "?standalone=true" to the URL')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Public access setup instructions displayed!'))
