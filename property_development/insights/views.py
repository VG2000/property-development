from django.conf import settings
from django.shortcuts import render


def insights_view(request):
    ctx = {
        "accommodation_survey_2023": settings.MEDIA_URL + "pdfs/accommodation_survey_2023.pdf",
        "domestic_stats": settings.MEDIA_URL + "pdfs/day_trips_2024.pdf",
    }
    return render(request, "insights.html", ctx)

def conwy_county_view(request):
    brochure_pdf = settings.MEDIA_URL + "pdfs/Destination-Conwy-Management-Plan-2019-2029.pdf"
    return render(request, "conwy_county.html", {"brochure_pdf": brochure_pdf})