from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path

from saas.models import *


def home_page_view(request):
    qs = PageVisit.objects.all()
    queryset = PageVisit.objects.filter(path=request.path)
    my_title = "This is a Page"
    my_context = {
        "page_title": my_title,
        "page_visit_count": queryset.count(),
        "percentage": (queryset.count() * 100.0) / qs.count(),
        "total_page_visit": qs.count(),
    }
    html_template = "home.html"
    path = request.path
    # print(path, "path")
    PageVisit.objects.create(path=request.path)
    return render(request, html_template, my_context)
