# projects/admin.py
from django.contrib import admin

from .models import Project, ProjectAccessLog


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title",)
    filter_horizontal = ("allowed_investors",)
    search_fields = ("title", "description")
    help_texts = {
        "brochure_url": "Only if not using a file. Prefer uploading a PDF to brochures/.",
    }

@admin.register(ProjectAccessLog)
class ProjectAccessLogAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "status", "ip", "ts")
    list_filter = ("status", "project")