from django.urls import path

from .views import ProjectListView, project_detail

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="projects-list"),
    path("projects/<int:pk>/", project_detail, name="project-detail"),
]