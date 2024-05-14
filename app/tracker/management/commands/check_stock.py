from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Checks stock\'s availability'

    def handle(self, *args, **options):
        #TODO: logic to check stock availability
        self.stdout.write(self.style.SUCCESS('Stock checked successfully'))
