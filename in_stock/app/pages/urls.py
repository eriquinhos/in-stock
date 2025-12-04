from django.urls import path

from . import views

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
    path("admin/users/", views.users_management_view, name="users_management"),
    path("admin/users/create/", views.create_user_view, name="create_user"),
    path(
        "admin/users/<int:user_id>/role/",
        views.update_user_role_view,
        name="update_user_role",
    ),
    path(
        "admin/users/<int:user_id>/toggle/",
        views.toggle_user_status_view,
        name="toggle_user_status",
    ),
    # Logs de auditoria
    path("admin/audit-logs/", views.audit_logs_view, name="audit_logs"),
    # Gerenciamento de empresas (apenas InStock admin)
    path("admin/companies/", views.companies_view, name="companies"),
    path("admin/companies/create/", views.create_company_view, name="create_company"),
    path(
        "admin/companies/<uuid:company_id>/",
        views.company_detail_view,
        name="company_detail",
    ),
]
