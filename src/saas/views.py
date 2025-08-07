from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from pathlib import Path
from saas.forms import *
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


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or None
        password = request.POST.get("password") or None

        if all([username, password]):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
    return render(request, "auth/login.html")

class UserDemoView(LoginRequiredMixin, TemplateView):
    template_name = 'demo.html'
    login_url = 'account_login'

# class UserLoginView(LoginView):
#     template_name = "auth/login.html"
#     authentication_form = CustomLoginForm
