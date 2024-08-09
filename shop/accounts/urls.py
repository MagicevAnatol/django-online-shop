from django.urls import path
from .views import (
    SignUpView,
    SignInView,
    SignOutView,
    UserProfileView,
    PasswordChangeView,
    AvatarUpdateView,
)

app_name = "accounts"

urlpatterns = [
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path("sign-in", SignInView.as_view(), name="sign-in"),
    path("sign-out", SignOutView.as_view(), name="sign-out"),
    path("profile", UserProfileView.as_view(), name="profile"),
    path("profile/password", PasswordChangeView.as_view(), name="change-password"),
    path("profile/avatar", AvatarUpdateView.as_view(), name="update-avatar"),
]
