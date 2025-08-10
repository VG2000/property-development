from django.conf import settings
from django.shortcuts import render


def insights_view(request):
    ctx = {
        "accommodation_survey_2023": settings.MEDIA_URL + "pdfs/accommodation_survey_2023.pdf",
        "domestic_stats": settings.MEDIA_URL + "pdfs/day_trips_2024.pdf",
    }
    return render(request, "insights.html", ctx)