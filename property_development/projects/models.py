# projects/models.py
from django.conf import settings
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

     # Only these users may view this project's page
    allowed_investors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="allowed_projects",
        help_text="Users who can view this project’s page"
    )

    def __str__(self):
        return self.title

    @property
    def brochure_src(self) -> str:
        """Prefer self-hosted file, fall back to external URL."""
        if self.brochure_file:
            return self.brochure_file.url
        return self.brochure_url or ""


class ProjectAccessLog(models.Model):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    STATUS_CHOICES = [(ALLOWED, "Allowed"), (DENIED, "Denied")]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    reason = models.CharField(max_length=100, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=255)
    ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["project", "ts", "status"])]