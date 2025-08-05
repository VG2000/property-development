from django.core.management.base import BaseCommand
from land_registry.models import PropertyProfile

class Command(BaseCommand):
    help = "Delete all PropertyProfile records"

    def handle(self, *args, **kwargs):
        count, _ = PropertyProfile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} PropertyProfile records."))
