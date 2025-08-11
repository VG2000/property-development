from django.urls import path

from . import views

urlpatterns = [
    path("insights/", views.insights_view, name="insights"),
    path("conwy-county/", views.conwy_county_view, name="conwy-county"),
]