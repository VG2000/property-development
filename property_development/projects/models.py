# projects/models.py
from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Optional spreadsheet sources (use either/or)
    sheet_url = models.URLField(blank=True)  # e.g. Google Sheets "Publish to web" embed link
    sheet_file = models.FileField(upload_to="spreadsheets/", blank=True, null=True)  # e.g. CSV

     # Optional brochure fields
    brochure_title = models.CharField(max_length=200, blank=True, default="Sales Brochure")
    brochure_file = models.FileField(upload_to="brochures/", blank=True, null=True)  # e.g. PDF in /media/brochures/
    brochure_url = models.URLField(blank=True)  # e.g. Google Drive/Sheets/External PDF (if you must)

    def __str__(self):
        return self.title

    @property
    def brochure_src(self) -> str:
        """Prefer self-hosted file, fall back to external URL."""
        if self.brochure_file:
            return self.brochure_file.url
        return self.brochure_url or ""