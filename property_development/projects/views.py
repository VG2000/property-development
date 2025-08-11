# projects/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Project
import csv, io

class ProjectListView(ListView):
    model = Project
    template_name = "projects_list.html"
    context_object_name = "projects"
    ordering = ["title"]

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    csv_preview = None
    # Very basic CSV preview (first 100 rows). Skip for non-CSV files.
    if project.sheet_file and project.sheet_file.name.lower().endswith(".csv"):
        project.sheet_file.open("rb")
        try:
            text = project.sheet_file.read().decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(text))
            rows = []
            for i, row in enumerate(reader):
                if i > 100:
                    break
                rows.append(row)
            headers = rows[0] if rows else []
            data = rows[1:] if len(rows) > 1 else []
            csv_preview = {"headers": headers, "rows": data}
        finally:
            project.sheet_file.close()

    link_map = {
    "Conwy County": "conwy-county",
    # "Day Trips Market – 2024": "day-trips-2024",
    # "Accommodation Survey 2023": "/insights/#accommodation"
}

    return render(
        request,
        "projects_detail.html",
        {"project": project, "csv_preview": csv_preview, "brochure_src": project.brochure_src, "link_map": link_map},
    )
