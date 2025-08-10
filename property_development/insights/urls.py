from django.urls import path

from . import views

urlpatterns = [
    path("insights/", views.insights_view, name="insights"),

]