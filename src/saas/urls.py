from django.urls import path
from .views import *
from django.conf.urls.static import static

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
    path("privacy-policy", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path(
        "terms-and-conditions",
        TermsAndConditionsView.as_view(),
        name="terms-and-condtion",
    ),
    path("signup-trial/", StartTrialView.as_view(), name="signup-trial"),
    path("schedule-demo/", ScheduleDemoView.as_view(), name="schedule_demo"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)