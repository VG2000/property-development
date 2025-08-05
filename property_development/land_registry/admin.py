from django.contrib import admin

from .models import LandRegistrySale, EPCRecord, PropertyProfile


@admin.register(LandRegistrySale)
class LandRegistrySaleAdmin(admin.ModelAdmin):
    search_fields = ("property__address","postcode")

@admin.register(EPCRecord)
class EPCRecordAdmin(admin.ModelAdmin):
    search_fields = ("postcode", "energy_rating")

@admin.register(PropertyProfile)
class PropertyProfileAdmin(admin.ModelAdmin):
    search_fields = ("property__address", "owner__name" )