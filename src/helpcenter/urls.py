from django.urls import path
from .views import HelpCenterView

app_name = "helpcenter"

urlpatterns = [
    path("", HelpCenterView.as_view(), name="help-center"),
]
