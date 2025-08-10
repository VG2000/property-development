from django.urls import path
from django.views.generic import TemplateView

from .views import map_data_htmx_view

urlpatterns = [
    path("map/", TemplateView.as_view(template_name="map.html"), name="map"),
    path("map-data/", map_data_htmx_view, name="map-data"),
]