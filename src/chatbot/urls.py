from django.urls import path
from .views import *


app_name = "chatbot"

urlpatterns = [
    path("api/chat/", chatbot, name="chatbot"),
]
