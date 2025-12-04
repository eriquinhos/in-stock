from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # Lista todos os usuários (GET) e cria um novo usuário (POST)
    path("", views.UserListCreateView.as_view(), name="user-list-create"),
    # Recupera um usuário específico (GET), atualiza (PUT/PATCH)
    # CORRIGIDO: path("<str:id>/") ao invés de path("/")
    path("<str:id>/", views.UserDetailView.as_view(), name="user-detail"),
    # Usa uma Template Genérica para uma página estática
    path(
        "create/",
        TemplateView.as_view(template_name="users/create.html"),
        name="user-create",
    ),
    path("register/", views.RegisterCreate.as_view(), name="user-register"),
    # Rota de Login (legado - usar /login/ ao invés de /users/login/)
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="users_login",
    ),
    # Rota de Logout (legado - usar /logout/ ao invés de /users/logout/)
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="users_logout",
    ),
    # Rota do MENU VERTICAL
    path(
        "menu/",
        TemplateView.as_view(template_name="MenuVertical.html"),
        name="MenuVertical",
    ),
]
