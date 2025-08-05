from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path

from saas.models import *


def home_view(request):
    return about_view(request)


def about_view(request):
    qs = PageVisit.objects.all()
    queryset = PageVisit.objects.filter(path=request.path)
    my_title = "This is a Page"
    try:
        percent = (queryset.count() * 100.0) / qs.count()
    except:
        percent = 0
    my_context = {
        "page_title": my_title,
        "page_visit_count": queryset.count(),
        "percentage": percent,
        "total_page_visit": qs.count(),
    }
    html_template = "home.html"
    path = request.path
    # print(path, "path")
    PageVisit.objects.create(path=request.path)
    return render(request, html_template, my_context)
 