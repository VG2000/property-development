import logging
import re

import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db.models import Max
from rapidfuzz import fuzz
from tqdm import tqdm

from land_registry.models import EPCRecord, LandRegistrySale, PropertyProfile

logger = logging.getLogger("land_registry")

class Command(BaseCommand):
    help = "Create PropertyProfile entries using latest Land Registry + EPC data"

    COMMON_NOISE_WORDS = [
    r"\bflat\b", r"\bapartment\b", r"\bapt\b", r"\bunit\b", r"\bthe\b", r"\bhouse\b",
    r"\bproperty\b", r"\bfarm\b", r"\bbungalow\b", r"\bvilla\b", r"\bold\b"
    ]

    ADDRESS_CLEANER = re.compile("|".join(COMMON_NOISE_WORDS), re.IGNORECASE)

    def handle(self, *args, **options):
        latest_sales = (
            LandRegistrySale.objects.values("postcode", "paon", "street")
            .annotate(latest_date=Max("deed_date"))
        )

        count, errors = 0, 0

        for sale_key in tqdm(latest_sales, desc="Processing sales", unit="record"):
            try:
                sale = LandRegistrySale.objects.get(
                    postcode=sale_key["postcode"],
                    paon=sale_key["paon"],
                    street=sale_key["street"],
                    deed_date=sale_key["latest_date"]
                )
                # print(f"Processing sale: {sale})")

                epc_qs = EPCRecord.objects.filter(postcode=sale.postcode)
                # print(f"EPCRecords: {epc_qs})")
                best_epc = self.best_match(epc_qs, sale)

                if not best_epc:
                    logger.warning(f"No EPC match for LR @ {sale.full_address}, {sale.postcode}")
                    continue

                # Use latest inspection date version of matching EPC
                epc = (
                    EPCRecord.objects.filter(postcode=sale.postcode, full_address=best_epc.full_address)
                    .order_by("-inspection_date")
                    .first()
                )

                if not epc or not epc.total_floor_area:
                    logger.warning(f"No usable EPC for {sale.full_address} — missing or no floor area.")
                    continue

                location = self.geocode_postcode(sale.postcode)
                floor_area = float(epc.total_floor_area)
                price = float(sale.price_paid)

                price_per_m2 = round(price / floor_area, 2)
                price_per_ft2 = round(price / self.convert_sq_m_to_sq_ft(floor_area), 2)
                estimated_beds = self.estimate_bedrooms(epc)

                PropertyProfile.objects.update_or_create(
                    postcode=sale.postcode,
                    paon=sale.paon,
                    street=sale.street,
                    defaults={
                        'land_registry_sale': sale,
                        'epc_record': epc,
                        'estimated_num_bedrooms': estimated_beds,
                        'location': location,
                        'price_per_sq_metre': price_per_m2,
                        'price_per_sq_ft': price_per_ft2,
                    }
                )
                count += 1
            except Exception as e:
                errors += 1
                logger.warning(f"Error processing sale {sale_key}: {e}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created/Updated {count} profiles. {errors} errors."))

    def clean_address(self, text):
        if not text:
            return ""
        text = re.sub(r"[-/]", " ", text)
        text = self.ADDRESS_CLEANER.sub("", text)
        text = re.sub(r"[^\w\s]", "", text).lower()
        return re.sub(r"\s+", " ", text).strip()

    def extract_numbers(self, text):
        return re.findall(r"\b\d+\b", text)

    def best_match(self, epc_queryset, sale_obj):
        sale_clean = self.clean_address(sale_obj.full_address)
        sale_tokens = set(sale_clean.split())
        sale_numbers = self.extract_numbers(sale_clean)
        sale_postcode = sale_obj.postcode.replace(" ", "").upper()

        # ---- Fast path: single number + same postcode ---------------------------
        if len(sale_numbers) == 1:
            for epc in epc_queryset:
                epc_clean = self.clean_address(epc.full_address)
                epc_numbers = self.extract_numbers(epc_clean)
                epc_postcode = epc.postcode.replace(" ", "").upper()

                if sale_numbers[0] in epc_numbers and sale_postcode == epc_postcode:
                    logger.info(
                        "[FastMatch] Number+postcode: LR='%s' ↔ EPC='%s'",
                        sale_obj.full_address, epc.full_address
                    )
                    return epc

        # ---- Fallback: fuzzy + hybrid boosts -----------------------------------
        best_score = 0.0
        best_epc = None

        for epc in epc_queryset:
            epc_clean = self.clean_address(epc.full_address)
            epc_tokens = set(epc_clean.split())
            epc_numbers = self.extract_numbers(epc_clean)

            # If LR has exactly one number and EPC doesn't contain it, skip early
            if len(sale_numbers) == 1 and sale_numbers[0] not in epc_numbers:
                continue

            base_score = fuzz.token_sort_ratio(sale_clean, epc_clean)
            score = float(base_score)
            boost_applied = []

            # Always check token-subset
            if sale_tokens and sale_tokens.issubset(epc_tokens):
                score += 15
                boost_applied.append("token_subset(+15)")

            # Add boost if LR token appears fully in EPC tokens (short-name boost)
            if any(token in epc_tokens for token in sale_tokens):
                score += 10
                boost_applied.append("token_overlap(+10)")

            # Substring and prefix boosts (only if base is halfway plausible)
            if base_score > 40:
                if sale_clean in epc_clean:
                    score += 20
                    boost_applied.append("substring(+20)")
                elif epc_clean.startswith(sale_clean):
                    score += 10
                    boost_applied.append("prefix(+10)")

            if score > 100:
                score = 100.0

            logger.info(
                "Fuzzy score=%.2f (base=%.2f%s) between LR='%s' and EPC='%s' (LR ID=%s, EPC PK=%s)",
                score,
                base_score,
                f", boosts={'+'.join(boost_applied)}" if boost_applied else "",
                sale_clean,
                epc_clean,
                getattr(sale_obj, 'pk', 'Unknown'),
                getattr(epc, 'pk', 'Unknown'),
            )

            if score > best_score:
                best_score = score
                best_epc = epc

        if best_epc and best_score >= 70:
            return best_epc

        # ---- Final fallback: Levenshtein ---------------------------------------
        best_lev_score = 0.0
        best_lev_epc = None

        for epc in epc_queryset:
            epc_raw = epc.full_address or ""
            sale_raw = sale_obj.full_address or ""

            lev_score = fuzz.ratio(sale_raw.lower(), epc_raw.lower())

            logger.info(
                "[LevenshteinFallback] Char score=%.2f between raw LR='%s' and EPC='%s'",
                lev_score,
                sale_raw,
                epc_raw,
            )

            if lev_score > best_lev_score:
                best_lev_score = lev_score
                best_lev_epc = epc

        if best_lev_score >= 90:
            logger.info(
                "[LevenshteinFallback] Accepted char match: score=%.2f, LR='%s', EPC='%s'",
                best_lev_score,
                sale_obj.full_address,
                best_lev_epc.full_address,
            )
            return best_lev_epc

        logger.error(
            "No EPC match for sale '%s' — best fuzzy score was %.2f, best Levenshtein %.2f",
            sale_obj.full_address,
            best_score,
            best_lev_score,
        )

        return None


    def geocode_postcode(self, postcode):
        try:
            response = requests.get(f"https://api.postcodes.io/postcodes/{postcode.replace(' ', '')}")
            if response.status_code == 200:
                result = response.json()['result']
                return Point(result['longitude'], result['latitude'])
        except Exception as e:
            logger.warning(f"Failed to geocode {postcode}: {e}")
        return None

    def estimate_bedrooms(self, epc) -> int:
        hab = epc.number_habitable_rooms
        typ = epc.property_type
        area = epc.total_floor_area

        if hab is None:
            logger.info(f"Missing habitable_rooms for EPC @ {epc.full_address}, pk={epc.pk}")
            return 1

        baseline = hab - 2
        if typ and typ.upper() in {"FLAT", "MAISONETTE"}:
            baseline = hab - 1
        elif typ.upper() == "TERRACED":
            baseline = hab - 1.5
        elif typ.upper() in {"DETACHED", "SEMI-DETACHED"}:
            baseline = hab - 2

        if area is not None:
            area = float(area)
            if area > 200:
                baseline += 1
            elif area < 50:
                baseline -= 1

        return max(min(round(baseline), hab), 1)

    def convert_sq_m_to_sq_ft(self, area_m2):
        return area_m2 * 10.7639
