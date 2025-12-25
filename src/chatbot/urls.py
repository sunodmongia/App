from django.urls import path
from .views import *


urlpatterns = [
    path("api/chat/", chatbot, name="chatbot"),
]
