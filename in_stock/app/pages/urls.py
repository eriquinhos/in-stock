from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Mapeia a URL '/login/' para a view de login embutida do Django
    path("login/", views.LoginCreateView.as_view(), name="login"),
    # Mapeia a URL para a view de logout embutida do Django
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
