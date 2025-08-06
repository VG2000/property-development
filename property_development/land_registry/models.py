from django.contrib.gis.db import models as gis_models
from django.db import models


class LandRegistrySale(models.Model):
    unique_id = models.CharField(max_length=64, primary_key=True)
    price_paid = models.IntegerField()
    deed_date = models.DateField()
    postcode = models.CharField(max_length=10)

    property_type = models.CharField(max_length=1)  # e.g. 'F', 'D', 'T'
    new_build = models.CharField(max_length=1)      # 'Y' or 'N'
    estate_type = models.CharField(max_length=1)    # 'F' or 'L'
    transaction_category = models.CharField(max_length=1)  # 'A' or 'B'

    # Address fields
    saon = models.CharField(max_length=100, blank=True)
    paon = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=255, blank=True)
    full_address = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    locality = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.postcode} - £{self.price_paid} ({self.deed_date})"


class EPCRecord(models.Model):
    lm_key = models.CharField(max_length=100, primary_key=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True)
    address3 = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=10)
    property_type = models.CharField(max_length=50, blank=True)
    built_form = models.CharField(max_length=50, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    total_floor_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    number_habitable_rooms = models.IntegerField(null=True, blank=True)
    number_heated_rooms = models.IntegerField(null=True, blank=True)
    uprn = models.CharField(max_length=100, blank=True, db_index=True)
    full_address = models.TextField(blank=True)


    def __str__(self):
        return f"{self.full_address} ({self.postcode})"


class PropertyProfile(models.Model):
    postcode = models.CharField(max_length=10)
    paon = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=255, blank=True)

    # Normalized fields
    estimated_num_bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    square_footage = models.IntegerField(null=True, blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Linked sources
    land_registry_sale = models.ForeignKey(LandRegistrySale, null=True, blank=True, on_delete=models.SET_NULL)
    epc_record = models.ForeignKey(EPCRecord, null=True, blank=True, on_delete=models.SET_NULL)

    # Optional future fields
    ons_lsoa = models.CharField(max_length=20, blank=True)
    rightmove_listing_id = models.CharField(max_length=50, blank=True)
    price_per_sq_ft = models.FloatField(null=True, blank=True)
    price_per_sq_metre = models.FloatField(null=True, blank=True)

    # Location field for GIS
    # This can be used to store the geolocation of the property
    # It can be a PointField or any other GIS field type as needed
    # For mapping
    location = gis_models.PointField(geography=True, null=True, blank=True)

    def __str__(self):
        return f"{self.paon} {self.street} ({self.postcode})"
