from django.urls import path
from .views import HelpCenterView

urlpatterns = [
    path("", HelpCenterView.as_view(), name="help-center"),
]
