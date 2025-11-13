from django.urls import path
from .views import *

urlpatterns = [
    path("help-center/", help_center, name="help-center"),
]
