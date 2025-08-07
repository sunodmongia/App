from django.urls import path
from .views import *

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("", HomeView.as_view(), name="home"),
    path("login/", login_view, name="login"),
    # path("about/", about_view),
    path("demo/", UserDemoView.as_view(), name="demo"),
    path("signup-trial/", StartTrialView.as_view(), name="signup-trial"),
    path("contact/", ScheduleDemoView.as_view(), name="schedule_demo"),
]
