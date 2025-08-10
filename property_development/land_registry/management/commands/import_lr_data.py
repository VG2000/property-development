import csv
import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from tqdm import tqdm

from land_registry.models import LandRegistrySale

logger = logging.getLogger("land_registry")

class Command(BaseCommand):
    help = "Import Land Registry Price Paid Data CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def parse_deed_date(self, date_str):
        """Parse date from CSV, handling DD/MM/YYYY and YYYY-MM-DD."""
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try DD/MM/YYYY
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            pass

        # Try YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

        # Still invalid
        return None

    def handle(self, *args, **kwargs):
        path = kwargs["csv_path"]
        count = 0
        total = self.get_line_count(path)

        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in tqdm(reader, total=total, desc="Importing LR Sales", unit="record"):
                deed_date = self.parse_deed_date(row.get("deed_date", ""))

                if not deed_date:
                    logger.warning(f"Invalid deed_date '{row.get('deed_date')}' for {row.get('unique_id')}")
                    continue  # Or set to a placeholder if you want

                LandRegistrySale.objects.update_or_create(
                    unique_id=row["unique_id"],
                    defaults={
                        "price_paid": int(row["price_paid"]),
                        "deed_date": deed_date,
                        "postcode": row["postcode"],
                        "property_type": row["property_type"],
                        "new_build": row["new_build"],
                        "estate_type": row["estate_type"],
                        "saon": row["saon"],
                        "paon": row["paon"],
                        "street": row["street"],
                        "locality": row["locality"],
                        "town": row["town"],
                        "district": row["district"],
                        "county": row["county"],
                        "transaction_category": row["transaction_category"],
                        "full_address": ", ".join(filter(None, [
                            row.get("saon", "").strip(),
                            row.get("paon", "").strip(),
                            row.get("street", "").strip(),
                        ])),
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} records"))

    def get_line_count(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            return sum(1 for _ in f) - 1  # minus header
