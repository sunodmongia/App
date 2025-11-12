from django.urls import path
from .views import MyProfileView, ProfileEditView, UserProfileView, ProfileListView

urlpatterns = [
    path("", MyProfileView.as_view(), name="profile-home"),
    path("<str:username>/", UserProfileView.as_view(), name="profile-home"),
    path("<int:pk>/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("all/", ProfileListView.as_view(), name="profile-list"),
]
