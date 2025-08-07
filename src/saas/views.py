from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from saas.forms import *
from saas.models import *


class HomeView(TemplateView):
    template_name = 'home.html'



# def about_view(request):
#     qs = PageVisit.objects.all()
#     queryset = PageVisit.objects.filter(path=request.path)
#     my_title = "This is a Page"
#     try:
#         percent = (queryset.count() * 100.0) / qs.count()
#     except:
#         percent = 0
#     my_context = {
#         "page_title": my_title,
#         "page_visit_count": queryset.count(),
#         "percentage": percent,
#         "total_page_visit": qs.count(),
#     }
#     html_template = "home.html"
#     path = request.path
#     # print(path, "path")
#     PageVisit.objects.create(path=request.path)
#     return render(request, html_template, my_context)


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
    template_name = "demo.html"
    login_url = "account_login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Demo'
        return context

class StartTrialView(LoginRequiredMixin, FormView):
    template_name = 'signup_trial.html'
    form_class = TrialSignupForm
    success_url = reverse_lazy('signup-trial')

    def form_valid(self, form):
        # Hash and save password
        instance = form.save(commit=False)
        raw_password = form.cleaned_data['password']
        instance.password_hash = make_password(raw_password)
        instance.save()
        messages.success(self.request, "Your free trial signup has been saved.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Start Trial"
        return context

class ScheduleDemoView(FormView):
    template_name = 'schedule_demo.html'
    form_class = DemoScheduleCallForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your demo scheduling request has been saved.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Schedule a Demo'
        return context


class ContactUsView(FormView):
    template_name = 'contact_us.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(f'{self.request}, Thanks for Contacting Us')
        return super().form_valid(form)