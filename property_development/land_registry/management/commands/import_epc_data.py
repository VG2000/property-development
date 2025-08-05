import csv
from django.core.management.base import BaseCommand
from land_registry.models import EPCRecord
from datetime import datetime
from tqdm import tqdm
import logging

logger = logging.getLogger('land_registry')

class Command(BaseCommand):
    help = "Import EPC data from CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['csv_path']
        count = 0
        total = self.get_line_count(path)
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=total, desc="Importing EPC Records", unit="record"):
                EPCRecord.objects.update_or_create(
                    lm_key=row["LMK_KEY"],
                    defaults={
                        "address1": row["ADDRESS1"],
                        "address2": row["ADDRESS2"],
                        "address3": row["ADDRESS3"],
                        "postcode": row["POSTCODE"],
                        "property_type": row["PROPERTY_TYPE"],
                        "built_form": row["BUILT_FORM"],
                        "inspection_date": parse_date_safe(row["INSPECTION_DATE"]),
                        "total_floor_area": parse_float(row["TOTAL_FLOOR_AREA"]),
                        "number_habitable_rooms": parse_int(row["NUMBER_HABITABLE_ROOMS"]),
                        "number_heated_rooms": parse_int(row["NUMBER_HEATED_ROOMS"]),
                        "uprn": row["UPRN"],
                        "full_address": row["ADDRESS"],
                    }
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported {count} EPC records"))

    def get_line_count(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f) - 1  # subtract header

def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def parse_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def parse_date_safe(val):
    try:
        return datetime.strptime(val, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None
