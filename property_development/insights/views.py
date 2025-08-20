from django.conf import settings
from django.shortcuts import render


def insights_view(request):
    return render(request, "north_wales.html")

def conwy_county_view(request):
    brochure_pdf = "https://website-public-bucket.s3.eu-west-2.amazonaws.com/wales-development/Destination-Conwy-Management-Plan-2019-2029.pdf"
    return render(request, "conwy_county.html", {"brochure_pdf": brochure_pdf})