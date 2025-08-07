from django.urls import path
from .views import *

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("", HomeView.as_view(), name="home"),
    path("login/", login_view, name="login"),
    path("demo/", UserDemoView.as_view(), name="demo"),
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('contact/', ContactUsView.as_view(), name='contact-us'),
    path("signup-trial/", StartTrialView.as_view(), name="signup-trial"),
    path("schedule-demo/", ScheduleDemoView.as_view(), name="schedule_demo"),
]
