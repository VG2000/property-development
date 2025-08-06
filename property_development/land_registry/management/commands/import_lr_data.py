import csv
import logging

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from tqdm import tqdm

from land_registry.models import LandRegistrySale

logger = logging.getLogger('land_registry')

class Command(BaseCommand):
    help = "Import Land Registry Price Paid Data CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['csv_path']
        count = 0
        total = self.get_line_count(path)
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=total, desc="Importing LR Sales", unit="record"):
                LandRegistrySale.objects.update_or_create(
                    unique_id=row['unique_id'],
                    defaults={
                        'price_paid': int(row['price_paid']),
                        'deed_date': parse_date(row['deed_date']),
                        'postcode': row['postcode'],
                        'property_type': row['property_type'],
                        'new_build': row['new_build'],
                        'estate_type': row['estate_type'],
                        'saon': row['saon'],
                        'paon': row['paon'],
                        'street': row['street'],
                        'locality': row['locality'],
                        'town': row['town'],
                        'district': row['district'],
                        'county': row['county'],
                        'transaction_category': row['transaction_category'],
                        "full_address": ", ".join(filter(None, [
                            row.get('saon', '').strip(),
                            row.get('paon', '').strip(),
                            row.get('street', '').strip(),
                        ]))
                    }
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported {count} records"))

    def get_line_count(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            return sum(1 for _ in f) - 1  # subtract header
