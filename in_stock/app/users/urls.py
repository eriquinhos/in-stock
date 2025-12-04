from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    # Lista todos os usuários (GET) e cria um novo usuário (POST)
    path("", views.UserListCreateView.as_view(), name="user-list-create"),

    # Recupera um usuário específico (GET), atualiza (PUT/PATCH)
    path("<int:id_user>/", views.UserDetailView.as_view(), name="user-detail"),

    # Usa uma Template Genérica para uma página estática
    path(
        "create/",
        TemplateView.as_view(template_name="users/create.html"),
        name="user-create",
    ),

    path("register/", views.RegisterCreate.as_view(), name="user-register"),
    
]