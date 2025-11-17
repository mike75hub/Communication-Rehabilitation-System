from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample probation officers for testing'

    def handle(self, *args, **options):
        officers_data = [
            {
                'username': 'officer.johnson',
                'email': 'johnson@probation.gov',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'user_type': 'officer',
                'department': 'Adult Probation',
                'badge_number': 'PO-001',
                'phone': '(555) 010-1001'
            },
            {
                'username': 'officer.smith',
                'email': 'smith@probation.gov',
                'first_name': 'Sarah',
                'last_name': 'Smith',
                'user_type': 'officer',
                'department': 'Juvenile Probation',
                'badge_number': 'PO-002',
                'phone': '(555) 010-1002'
            },
            {
                'username': 'officer.garcia',
                'email': 'garcia@probation.gov',
                'first_name': 'Carlos',
                'last_name': 'Garcia',
                'user_type': 'officer',
                'department': 'Drug Court',
                'badge_number': 'PO-003',
                'phone': '(555) 010-1003'
            },
            {
                'username': 'officer.williams',
                'email': 'williams@probation.gov',
                'first_name': 'Lisa',
                'last_name': 'Williams',
                'user_type': 'officer',
                'department': 'Community Supervision',
                'badge_number': 'PO-004',
                'phone': '(555) 010-1004'
            }
        ]

        created_count = 0
        for officer_data in officers_data:
            username = officer_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=officer_data['email'],
                    password='probation123',  # Default password
                    first_name=officer_data['first_name'],
                    last_name=officer_data['last_name'],
                    user_type=officer_data['user_type'],
                    department=officer_data['department'],
                    badge_number=officer_data['badge_number'],
                    phone=officer_data['phone'],
                    is_active_officer=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created probation officer: {user.get_full_name()}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'Officer already exists: {username}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} probation officers')
        )