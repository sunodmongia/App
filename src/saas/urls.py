from django.urls import path
from .views import *

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("blog/", BlogView.as_view(), name="blog"),
    path("demo/", UserDemoView.as_view(), name="demo"),
    path("pricing/", PricingView.as_view(), name="pricing"),
    path("case-studies", CaseStudyView.as_view(), name="case-studies"),
    path("contact/", ContactUsView.as_view(), name="contact-us"),
    path("api/", APIView.as_view(), name="api-view"),
    path("features", FeaturesView.as_view(), name="features"),
    path('privacy-policy', PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("help-center/", HelpCenterView.as_view(), name="help-center"),
    path("signup-trial/", StartTrialView.as_view(), name="signup-trial"),
    path("schedule-demo/", ScheduleDemoView.as_view(), name="schedule_demo"),
]
