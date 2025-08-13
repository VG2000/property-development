# projects/views.py
import csv
import io

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .models import Project, ProjectAccessLog


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects_list.html"
    context_object_name = "projects"
    ordering = ["title"]
    login_url = "login"            
    redirect_field_name = "next"

    # Only show projects the user is allowed to see
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(allowed_investors=self.request.user)


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")

def _log(request, project, allowed, reason=""):
        ProjectAccessLog.objects.create(
        project=project,
        user=request.user if request.user.is_authenticated else None,
        status=ProjectAccessLog.ALLOWED if allowed else ProjectAccessLog.DENIED,
        reason=reason,
        ip=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        path=request.get_full_path(),
    )

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    is_allowed = (
        request.user.is_staff
        or project.allowed_investors.filter(pk=request.user.pk).exists()
    )

    if not is_allowed:
        _log(request, project, allowed=False, reason="not_invited")
        return HttpResponseForbidden("You have not been invited to view this project.")

    _log(request, project, allowed=True)

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
