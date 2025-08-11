# projects/admin.py
from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "description")
    fields = ("title", "description", "brochure_title", "brochure_file", "brochure_url", "sheet_url", "sheet_file")
    help_texts = {
        "brochure_url": "Only if not using a file. Prefer uploading a PDF to brochures/.",
    }
