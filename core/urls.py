from django.urls import path
from .views import LoginView, MeView, RefreshView, RegisterView
urlpatterns = [path("auth/register/", RegisterView.as_view()), path("auth/login/", LoginView.as_view()), path("auth/refresh/", RefreshView.as_view()), path("auth/me/", MeView.as_view())]
