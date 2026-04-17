from django.urls import path
from .views import MyProfileView, ProfileEditView, UserProfileView, ProfileListView, ProfileDeleteView

app_name = "profiles"

urlpatterns = [
    path("", MyProfileView.as_view(), name="profile-home"),
    path("all/", ProfileListView.as_view(), name="profile-list"),
    path("u/<str:username>/", UserProfileView.as_view(), name="profile-user"),
    path("<int:pk>/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("<int:pk>/delete/", ProfileDeleteView.as_view(), name="profile-delete"),
]
