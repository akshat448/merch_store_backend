from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a fixed admin user if it does not exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        fixed_email = 'admin@example.com'
        fixed_password = 'SuPeRaDmIn'

        if not User.objects.filter(email=fixed_email).exists():
            User.objects.create_superuser(email=fixed_email, password=fixed_password)
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))
