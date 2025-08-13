from django.urls import path

from .views import ProjectListView, project_detail

urlpatterns = [
    path("", ProjectListView.as_view(), name="projects-list"),
    path("<int:pk>/", project_detail, name="project-detail"),
]