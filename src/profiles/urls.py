from django.urls import path
from profiles.views import *


urlpatterns = [
    path("<username>", user_profiles, name="profile"),

]
