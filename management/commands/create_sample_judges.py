from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample judges for testing'

    def handle(self, *args, **options):
        judges_data = [
            {
                'username': 'judge.wilson',
                'email': 'wilson@courts.gov',
                'first_name': 'Robert',
                'last_name': 'Wilson',
                'user_type': 'judge',
                'court_jurisdiction': 'Circuit Court - District 1',
                'phone': '(555) 010-2001'
            },
            {
                'username': 'judge.martinez',
                'email': 'martinez@courts.gov',
                'first_name': 'Maria',
                'last_name': 'Martinez',
                'user_type': 'judge',
                'court_jurisdiction': 'Family Court',
                'phone': '(555) 010-2002'
            },
            {
                'username': 'judge.thompson',
                'email': 'thompson@courts.gov',
                'first_name': 'James',
                'last_name': 'Thompson',
                'user_type': 'judge',
                'court_jurisdiction': 'Drug Court',
                'phone': '(555) 010-2003'
            }
        ]

        created_count = 0
        for judge_data in judges_data:
            username = judge_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=judge_data['email'],
                    password='judge123',  # Default password
                    first_name=judge_data['first_name'],
                    last_name=judge_data['last_name'],
                    user_type=judge_data['user_type'],
                    court_jurisdiction=judge_data['court_jurisdiction'],
                    phone=judge_data['phone']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created judge: Honorable {user.get_full_name()}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'Judge already exists: {username}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} judges')
        )