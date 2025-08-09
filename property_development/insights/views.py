from django.shortcuts import render


def insights_view(request):
    return render(request, "insights.html")