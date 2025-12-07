from django.urls import path

from . import views

from in_stock.app.products.views import (
    ProductListCreateView,
    ProductUpdateView,
    ProductDeleteView,
    CategoryListCreateView,
    CategoryUpdateView,
    CategoryDeleteView
)

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    
    # Mapeia a URL '/login/' para a view de login
    path("login/", views.LoginCreateView.as_view(), name="login"),
    # Mapeia a URL para a view de logout
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # Solicitar acesso (empresas que querem usar o InStock)
    path("request-access/", views.RequestAccessView.as_view(), name="request_access"),
    # Troca de senha obrigatória no primeiro login
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    # Gerenciamento de solicitações (apenas admins InStock)
    path("access-requests/", views.access_requests_view, name="access_requests"),
    path(
        "access-requests/<uuid:request_id>/approve/",
        views.approve_request_view,
        name="approve_request",
    ),
    path(
        "access-requests/<uuid:request_id>/reject/",
        views.reject_request_view,
        name="reject_request",
    ),
    # Redireciona registro antigo para solicitar acesso
    path("register/", views.PublicRegisterView.as_view(), name="register"),
    # Redefinição de senha
    path(
        "forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"
    ),
    path(
        "reset-password/<str:token>/",
        views.ResetPasswordView.as_view(),
        name="reset_password",
    ),
    # ============================================
    # GESTÃO DE USUÁRIOS E EMPRESAS
    # ============================================
    # Gerenciamento de usuários
    path("gestao/usuarios/", views.users_management_view, name="users_management"),
    path("gestao/usuarios/criar/", views.create_user_view, name="create_user"),
    path(
        "gestao/usuarios/<int:user_id>/role/",
        views.update_user_role_view,
        name="update_user_role",
    ),
    path(
        "gestao/usuarios/<int:user_id>/toggle/",
        views.toggle_user_status_view,
        name="toggle_user_status",
    ),
    # Logs de auditoria
    path("gestao/auditoria/", views.audit_logs_view, name="audit_logs"),
    # Gerenciamento de empresas (apenas InStock admin)
    path("gestao/empresas/", views.companies_view, name="companies"),
    path("gestao/empresas/criar/", views.create_company_view, name="create_company"),
    path(
        "gestao/empresas/<uuid:company_id>/",
        views.company_detail_view,
        name="company_detail",
    ),

    # ============================================
    # GESTÃO DE PRODUTOS (Usando os imports novos)
    # ============================================
    # Note o uso de .as_view() porque são Classes
    
    path("gestao/produtos/", ProductListCreateView.as_view(), name="product-list-create"),
    path("gestao/produtos/<int:id_product>/editar/", ProductUpdateView.as_view(), name="product-update"),
    path("gestao/produtos/<int:id_product>/deletar/", ProductDeleteView.as_view(), name="product-delete"),
    # ============================================
    # GESTÃO DE CATEGORIAS
    # ============================================
    
    path("gestao/categorias/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("gestao/categorias/<int:id_category>/editar/", CategoryUpdateView.as_view(), name="category-update"),
    path("gestao/categorias/<int:id_category>/deletar/", CategoryDeleteView.as_view(), name="category-delete"),
]
