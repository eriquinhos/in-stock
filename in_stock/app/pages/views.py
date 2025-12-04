import secrets
from datetime import timedelta
from decimal import Decimal

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.utils import timezone
from django.views import View

import in_stock.config.settings as settings
from in_stock.app.pages.forms import LoginForm
from in_stock.app.products.models import Category, Product
from in_stock.app.reports.models import Report
from in_stock.app.sales.models import Sale
from in_stock.app.suppliers.models import Supplier
from in_stock.app.users.audit_service import AuditService
from in_stock.app.users.forms import CustomUserCreationForm
from in_stock.app.users.models import (
    AccessRequest,
    AuditLog,
    Company,
    CustomUser,
    PasswordResetToken,
    Role,
)


def home(request):
    return render(request, "pages/index.html")


def dashboard_view(request):
    # Acesso apenas para autenticados
    if not request.user.is_authenticated:
        return render(request, "errors/401.html")

    # Verifica se precisa trocar a senha
    if request.user.must_change_password:
        return redirect("change_password")

    today = timezone.now()

    # === MÉTRICAS PRINCIPAIS ===
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_sales = Sale.objects.count()
    total_reports = Report.objects.count()
    total_categories = Category.objects.count()

    # Quantidade total de produtos em estoque
    total_stock = Product.objects.aggregate(total=Sum("quantity"))["total"] or 0

    # Valor total do estoque (quantidade * preço)
    stock_value = Product.objects.aggregate(
        total=Sum(F("quantity") * F("price"), output_field=DecimalField())
    )["total"] or Decimal("0.00")

    # === MOVIMENTAÇÕES ===
    # Movimentações do mês atual
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    sales_this_month = Sale.objects.filter(date__gte=first_day_of_month).count()

    # Movimentações do mês anterior (para comparação)
    first_day_last_month = (first_day_of_month - timedelta(days=1)).replace(day=1)
    sales_last_month = Sale.objects.filter(
        date__gte=first_day_last_month, date__lt=first_day_of_month
    ).count()

    # Calcular variação percentual
    if sales_last_month > 0:
        sales_variation = (
            (sales_this_month - sales_last_month) / sales_last_month
        ) * 100
    else:
        sales_variation = 100 if sales_this_month > 0 else 0

    # Entradas e saídas totais
    entries = Sale.objects.filter(type="entry").count()
    exits = Sale.objects.filter(type="exits").count()

    # Entradas e saídas do mês
    entries_this_month = Sale.objects.filter(
        type="entry", date__gte=first_day_of_month
    ).count()
    exits_this_month = Sale.objects.filter(
        type="exits", date__gte=first_day_of_month
    ).count()

    # === GRÁFICO: Movimentações dos últimos 7 dias ===
    seven_days_ago = today - timedelta(days=7)
    daily_movements = []

    for i in range(7):
        day = (today - timedelta(days=6 - i)).date()
        day_entries = Sale.objects.filter(type="entry", date__date=day).count()
        day_exits = Sale.objects.filter(type="exits", date__date=day).count()
        daily_movements.append(
            {
                "date": day.strftime("%d/%m"),
                "day_name": day.strftime("%a"),
                "entries": day_entries,
                "exits": day_exits,
            }
        )

    # === ALERTAS ===
    # Produtos com baixo estoque (menos de 10 unidades)
    low_stock_products = Product.objects.filter(quantity__lt=10).order_by("quantity")[
        :5
    ]
    low_stock_count = Product.objects.filter(quantity__lt=10).count()

    # Produtos próximos do vencimento (próximos 30 dias)
    thirty_days_from_now = today.date() + timedelta(days=30)
    expiring_soon = Product.objects.filter(
        expiration_date__lte=thirty_days_from_now, expiration_date__gte=today.date()
    ).order_by("expiration_date")[:5]
    expiring_count = Product.objects.filter(
        expiration_date__lte=thirty_days_from_now, expiration_date__gte=today.date()
    ).count()

    # Produtos já vencidos
    expired_products = Product.objects.filter(
        expiration_date__lt=today.date()
    ).order_by("expiration_date")[:5]
    expired_count = Product.objects.filter(expiration_date__lt=today.date()).count()

    # === TOP PRODUTOS ===
    # Produtos mais movimentados (com mais saídas)
    top_products = Product.objects.annotate(
        movement_count=Count("sale_product")
    ).order_by("-movement_count")[:5]

    # Categorias com mais produtos
    top_categories = Category.objects.annotate(
        product_count=Count("products_category")
    ).order_by("-product_count")[:5]

    # === MOVIMENTAÇÕES RECENTES ===
    recent_sales = Sale.objects.select_related("product", "user").order_by("-date")[:5]

    # === SOLICITAÇÕES PENDENTES (Admin) ===
    pending_requests_count = 0
    pending_requests = []
    if request.user.is_instock_admin:
        # InStock Admin vê solicitações de novas empresas
        pending_requests = AccessRequest.objects.filter(
            status="pending", request_type="new_company"
        )
        pending_requests_count = pending_requests.count()
    elif request.user.is_company_admin and request.user.company_obj:
        # Company Admin vê solicitações para sua empresa
        pending_requests = AccessRequest.objects.filter(
            status="pending",
            request_type="join_company",
            company=request.user.company_obj,
        )
        pending_requests_count = pending_requests.count()

    context = {
        # Métricas principais
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_sales": total_sales,
        "total_reports": total_reports,
        "total_categories": total_categories,
        "total_stock": total_stock,
        "stock_value": stock_value,
        # Movimentações
        "sales_this_month": sales_this_month,
        "sales_last_month": sales_last_month,
        "sales_variation": round(sales_variation, 1),
        "entries": entries,
        "exits": exits,
        "entries_this_month": entries_this_month,
        "exits_this_month": exits_this_month,
        # Gráfico de 7 dias
        "daily_movements": daily_movements,
        # Alertas
        "low_stock_products": low_stock_products,
        "low_stock_count": low_stock_count,
        "expiring_soon": expiring_soon,
        "expiring_count": expiring_count,
        "expired_products": expired_products,
        "expired_count": expired_count,
        # Top produtos e categorias
        "top_products": top_products,
        "top_categories": top_categories,
        # Movimentações recentes
        "recent_sales": recent_sales,
        # Admin
        "pending_requests_count": pending_requests_count,
        "pending_requests": pending_requests,
        # === MÉTRICAS DE EFICIÊNCIA (para impressionar empresas) ===
        # Taxa de rotatividade (giro de estoque)
        "stock_turnover": (
            round((exits / total_stock * 100), 1) if total_stock > 0 else 0
        ),
        # Produtos saudáveis (com estoque adequado e não vencidos)
        "healthy_products": total_products - low_stock_count - expired_count,
        "health_percentage": (
            round(
                (
                    (total_products - low_stock_count - expired_count)
                    / total_products
                    * 100
                ),
                1,
            )
            if total_products > 0
            else 100
        ),
        # Perdas evitadas (produtos com alertas ativos que foram identificados)
        "potential_savings": (
            round(float(stock_value) * 0.05, 2)
            if expired_count > 0 or expiring_count > 0
            else 0
        ),
        # Eficiência operacional (movimentações vs produtos)
        "efficiency_rate": (
            round((total_sales / total_products * 100), 1) if total_products > 0 else 0
        ),
        # Média de movimentações por dia (últimos 7 dias)
        "avg_daily_movements": round(
            sum([d["entries"] + d["exits"] for d in daily_movements]) / 7, 1
        ),
    }
    return render(request, "pages/dashboard.html", context)


class LoginCreateView(View):
    template_name = "auth/login.html"

    def get(self, request):
        # Se já está logado
        if request.user.is_authenticated:
            if request.user.must_change_password:
                return redirect("change_password")
            return redirect("dashboard")
        return render(request, self.template_name)

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # Verifica se o usuário está ativo (is_staff)
                if not user.is_staff and not user.is_superuser:
                    messages.error(
                        request,
                        "Sua conta está desativada. Entre em contato com o administrador.",
                    )
                    return render(request, self.template_name)

                login(request, user)
                # Verifica se precisa trocar a senha
                if user.must_change_password:
                    return redirect("change_password")
                return redirect("dashboard")

            else:
                messages.error(request, "E-mail ou senha incorretos.")
        return render(request, self.template_name)


class LogoutView(View):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)

        return redirect("login")


def error_403_view(request, exception=None):
    # Passamos status=403 para garantir que o navegador/servidor saiba que é um erro 403
    return render(request, "errors/403.html", status=403)


# ============================================
# VIEWS DE SOLICITAÇÃO DE ACESSO
# ============================================


class RequestAccessView(View):
    """
    View pública para solicitar acesso ao sistema.

    Dois tipos de solicitação:
    1. new_company: Nova empresa querendo usar o sistema
    2. join_company: Usuário querendo entrar em empresa existente
    """

    template_name = "auth/request_access.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")

        # Lista empresas ativas para o formulário de join_company
        companies = Company.objects.filter(is_active=True).order_by("name")

        return render(
            request,
            self.template_name,
            {
                "companies": companies,
            },
        )

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")

        request_type = request.POST.get("request_type", "new_company")
        name = request.POST.get("name", "").strip()
        personal_email = request.POST.get("personal_email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        # Campos específicos por tipo
        company_name = request.POST.get("company_name", "").strip()
        cnpj = request.POST.get("cnpj", "").strip()
        company_id = request.POST.get("company_id", "")

        # Validações comuns
        if not all([name, personal_email]):
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
            return self.get(request)

        # Verifica se já existe solicitação pendente
        if AccessRequest.objects.filter(
            personal_email=personal_email, status="pending"
        ).exists():
            messages.warning(
                request, "Já existe uma solicitação pendente com este email."
            )
            return self.get(request)

        # Verifica se já existe usuário com este email
        if CustomUser.objects.filter(email=personal_email).exists():
            messages.warning(
                request, "Este email já possui uma conta. Tente fazer login."
            )
            return redirect("login")

        if request_type == "new_company":
            # Validações específicas para nova empresa
            if not all([company_name, cnpj]):
                messages.error(request, "Para nova empresa, informe o nome e CNPJ.")
                return self.get(request)

            # Verifica se já existe empresa com este CNPJ
            if Company.objects.filter(cnpj=cnpj).exists():
                messages.warning(
                    request, "Já existe uma empresa cadastrada com este CNPJ."
                )
                return self.get(request)

            # Cria a solicitação de nova empresa
            AccessRequest.objects.create(
                request_type="new_company",
                name=name,
                personal_email=personal_email,
                company_name=company_name,
                cnpj=cnpj,
                phone=phone,
                message=message,
            )

            messages.success(
                request,
                "Sua solicitação de cadastro de empresa foi enviada! Você receberá um email quando for aprovada.",
            )
        else:
            # Validações específicas para entrar em empresa
            if not company_id:
                messages.error(request, "Por favor, selecione uma empresa.")
                return self.get(request)

            try:
                company = Company.objects.get(id=company_id, is_active=True)
            except Company.DoesNotExist:
                messages.error(request, "Empresa não encontrada.")
                return self.get(request)

            # Cria a solicitação de entrar na empresa (sem cargo - admin define depois)
            AccessRequest.objects.create(
                request_type="join_company",
                name=name,
                personal_email=personal_email,
                company=company,
                phone=phone,
                message=message,
            )

            messages.success(
                request,
                f"Sua solicitação para entrar em {company.name} foi enviada! Você receberá um email quando for aprovada.",
            )

        return redirect("login")


class ChangePasswordView(View):
    """View para troca obrigatória de senha no primeiro acesso"""

    template_name = "auth/change_password.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.must_change_password:
            return redirect("dashboard")
        return render(request, self.template_name)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if new_password != confirm_password:
            messages.error(request, "As senhas não coincidem.")
            return render(request, self.template_name)

        if len(new_password) < 6:
            messages.error(request, "A senha deve ter pelo menos 6 caracteres.")
            return render(request, self.template_name)

        # Atualiza a senha
        request.user.set_password(new_password)
        request.user.must_change_password = False
        request.user.save()

        # Faz login novamente com a nova senha
        login(request, request.user)
        messages.success(request, "Senha alterada com sucesso! Bem-vindo ao InStock.")
        return redirect("dashboard")


@login_required
def access_requests_view(request):
    """
    Lista todas as solicitações de acesso.
    - InStock Admin: Vê todas (foco nas new_company)
    - Company Admin: Vê apenas as da sua empresa (join_company)
    """
    if not request.user.can_approve_access_requests():
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("dashboard")

    if request.user.is_instock_admin:
        # InStock Admin vê solicitações de novas empresas
        pending = AccessRequest.objects.filter(
            status="pending", request_type="new_company"
        )
        approved = AccessRequest.objects.filter(
            status="approved", request_type="new_company"
        ).order_by("-updated_at")[:20]
        rejected = AccessRequest.objects.filter(
            status="rejected", request_type="new_company"
        ).order_by("-updated_at")[:20]
    else:
        # Company Admin vê solicitações para sua empresa
        pending = AccessRequest.objects.filter(
            status="pending",
            request_type="join_company",
            company=request.user.company_obj,
        )
        approved = AccessRequest.objects.filter(
            status="approved",
            request_type="join_company",
            company=request.user.company_obj,
        ).order_by("-updated_at")[:20]
        rejected = AccessRequest.objects.filter(
            status="rejected",
            request_type="join_company",
            company=request.user.company_obj,
        ).order_by("-updated_at")[:20]

    context = {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "pending_requests_count": pending.count(),
        "is_instock_admin": request.user.is_instock_admin,
    }
    return render(request, "pages/access_requests.html", context)


@login_required
def approve_request_view(request, request_id):
    """
    Aprova uma solicitação de acesso.
    - new_company: Cria empresa + admin da empresa
    - join_company: Cria usuário na empresa existente
    """
    access_request = get_object_or_404(AccessRequest, id=request_id)

    # Verifica permissão
    if access_request.request_type == "new_company":
        if not request.user.is_instock_admin:
            messages.error(
                request,
                "Você não tem permissão para aprovar solicitações de novas empresas.",
            )
            return redirect("dashboard")
    else:  # join_company
        if (
            not request.user.is_company_admin
            or access_request.company != request.user.company_obj
        ):
            messages.error(
                request, "Você não tem permissão para aprovar esta solicitação."
            )
            return redirect("dashboard")

    if access_request.status != "pending":
        messages.warning(request, "Esta solicitação já foi processada.")
        return redirect("access_requests")

    if access_request.request_type == "new_company":
        # === NOVA EMPRESA ===
        # Cria a empresa
        company, created = Company.objects.get_or_create(
            cnpj=access_request.cnpj,
            defaults={
                "name": access_request.company_name,
                "phone": access_request.phone,
            },
        )

        # Gera email e senha
        generated_email = AccessRequest.generate_company_email(
            access_request.name, access_request.company_name
        )
        generated_password = AccessRequest.generate_password()

        # Verifica se o email já existe e adiciona número se necessário
        base_email = generated_email
        counter = 1
        while CustomUser.objects.filter(email=generated_email).exists():
            parts = base_email.split("@")
            generated_email = f"{parts[0]}{counter}@{parts[1]}"
            counter += 1

        # Cria o usuário admin da empresa
        new_user = CustomUser.objects.create_user(
            email=generated_email,
            password=generated_password,
            name=access_request.name,
            company=access_request.company_name,
            company_obj=company,
            role="company_admin",  # Admin da empresa
            must_change_password=True,
        )

        # Log de auditoria
        AuditService.log_approve(
            request.user,
            access_request,
            request,
            new_user_email=generated_email,
            company_name=company.name,
        )

        success_message = f"✅ Empresa e Admin criados! Email: {generated_email} | Senha: {generated_password}"

    else:
        # === ENTRAR EM EMPRESA EXISTENTE ===
        company = access_request.company

        # Gera senha
        generated_password = AccessRequest.generate_password()
        generated_email = access_request.personal_email  # Usa o email pessoal

        # Pega o cargo escolhido pelo admin (via POST)
        selected_role = request.POST.get("role", "operator")
        if selected_role not in ["manager", "operator"]:
            selected_role = "operator"

        # Cria o usuário
        new_user = CustomUser.objects.create_user(
            email=generated_email,
            password=generated_password,
            name=access_request.name,
            company=company.name if company else None,
            company_obj=company,
            role=selected_role,  # Cargo escolhido pelo admin
            must_change_password=True,
        )

        role_display = "Gestor" if selected_role == "manager" else "Operador"

        # Log de auditoria
        AuditService.log_approve(
            request.user,
            access_request,
            request,
            new_user_email=generated_email,
            role=selected_role,
        )

        success_message = (
            f"✅ Usuário criado como {role_display}! Senha: {generated_password}"
        )

    # Atualiza a solicitação
    access_request.status = "approved"
    access_request.generated_email = generated_email
    access_request.generated_password = generated_password
    access_request.approved_by = request.user
    access_request.save()

    # Tenta enviar email
    try:
        send_mail(
            subject="InStock - Sua conta foi aprovada!",
            message=f"""
Olá {access_request.name},

Sua solicitação de acesso ao InStock foi aprovada!

Seus dados de acesso:
📧 Email: {generated_email}
🔑 Senha temporária: {generated_password}

Acesse: https://www.instock.app.br/login/

⚠️ No primeiro acesso, você será solicitado a alterar sua senha.

Atenciosamente,
Equipe InStock
            """,
            from_email=getattr(
                django_settings, "DEFAULT_FROM_EMAIL", "noreply@instock.app.br"
            ),
            recipient_list=[access_request.personal_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

    messages.success(request, success_message)
    return redirect("access_requests")


@login_required
def reject_request_view(request, request_id):
    """Rejeita uma solicitação de acesso"""
    access_request = get_object_or_404(AccessRequest, id=request_id)

    # Verifica permissão
    if access_request.request_type == "new_company":
        if not request.user.is_instock_admin:
            messages.error(
                request,
                "Você não tem permissão para rejeitar solicitações de novas empresas.",
            )
            return redirect("dashboard")
    else:  # join_company
        if (
            not request.user.is_company_admin
            or access_request.company != request.user.company_obj
        ):
            messages.error(
                request, "Você não tem permissão para rejeitar esta solicitação."
            )
            return redirect("dashboard")

    if access_request.status != "pending":
        messages.warning(request, "Esta solicitação já foi processada.")
        return redirect("access_requests")

    access_request.status = "rejected"
    access_request.rejection_reason = request.POST.get("reason", "")
    access_request.save()

    messages.success(request, "❌ Solicitação rejeitada.")
    return redirect("access_requests")


# Manter a view antiga de registro público removida/comentada
# pois agora usamos o fluxo de solicitação de acesso
class PublicRegisterView(View):
    """View pública para registro - Redireciona para solicitar acesso"""

    def get(self, request):
        return redirect("request_access")

    def post(self, request):
        return redirect("request_access")


# ============================================
# VIEWS DE REDEFINIÇÃO DE SENHA
# ============================================


class ForgotPasswordView(View):
    """View para solicitar redefinição de senha"""

    template_name = "auth/forgot_password.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")

        email = request.POST.get("email", "").strip().lower()

        if not email:
            return render(
                request, self.template_name, {"error": "Por favor, informe seu email."}
            )

        # Busca o usuário pelo email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Por segurança, não revelamos se o email existe ou não
            return render(
                request,
                self.template_name,
                {
                    "success": True,
                    "message": "Se este email estiver cadastrado, você receberá um link de redefinição.",
                },
            )

        # Cria o token de redefinição
        token = PasswordResetToken.create_for_user(user)

        # Monta o link de redefinição
        reset_link = request.build_absolute_uri(f"/reset-password/{token.token}/")

        # Tenta enviar o email
        try:
            from django.template.loader import render_to_string

            html_message = render_to_string(
                "emails/password_reset.html",
                {
                    "user_name": user.name,
                    "reset_link": reset_link,
                },
            )

            send_mail(
                subject="Redefinição de Senha - InStock",
                message=f"""
Olá {user.name},

Recebemos uma solicitação para redefinir sua senha.

Clique no link abaixo para criar uma nova senha:
{reset_link}

Este link expira em 1 hora.

Se você não solicitou isso, ignore este email.

Atenciosamente,
Equipe InStock
                """,
                from_email=getattr(
                    django_settings, "DEFAULT_FROM_EMAIL", "noreply@instock.app.br"
                ),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erro ao enviar email de redefinição: {e}")

        # Mostra mensagem de sucesso
        return render(
            request,
            self.template_name,
            {
                "success": True,
                "message": "Se este email estiver cadastrado, você receberá um link de redefinição.",
            },
        )


class ResetPasswordView(View):
    """View para redefinir a senha usando o token"""

    template_name = "auth/reset_password.html"

    def get(self, request, token):
        if request.user.is_authenticated:
            return redirect("dashboard")

        # Verifica se o token é válido
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid:
                return render(request, self.template_name, {"invalid_token": True})
        except PasswordResetToken.DoesNotExist:
            return render(request, self.template_name, {"invalid_token": True})

        return render(request, self.template_name, {"token": token})

    def post(self, request, token):
        if request.user.is_authenticated:
            return redirect("dashboard")

        # Verifica se o token é válido
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid:
                return render(request, self.template_name, {"invalid_token": True})
        except PasswordResetToken.DoesNotExist:
            return render(request, self.template_name, {"invalid_token": True})

        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        # Validações
        if not password or not password_confirm:
            return render(
                request,
                self.template_name,
                {"token": token, "error": "Por favor, preencha todos os campos."},
            )

        if password != password_confirm:
            return render(
                request,
                self.template_name,
                {"token": token, "error": "As senhas não coincidem."},
            )

        if len(password) < 8:
            return render(
                request,
                self.template_name,
                {"token": token, "error": "A senha deve ter pelo menos 8 caracteres."},
            )

        # Atualiza a senha do usuário
        user = reset_token.user
        user.set_password(password)
        user.must_change_password = False  # Não precisa mais trocar
        user.save()

        # Marca o token como usado
        reset_token.used = True
        reset_token.save()

        messages.success(
            request, "Senha redefinida com sucesso! Faça login com sua nova senha."
        )
        return redirect("login")


# ============================================
# VIEWS DE GESTÃO DE USUÁRIOS E EMPRESAS
# ============================================


@login_required
def users_management_view(request):
    """View para gerenciamento de usuários (apenas admins)"""
    if not request.user.can_manage_users():
        messages.error(request, "Você não tem permissão para gerenciar usuários.")
        return redirect("dashboard")

    # InStock admin vê todos os usuários
    if request.user.is_instock_admin:
        users = CustomUser.objects.all().select_related("company_obj")
        companies = Company.objects.all()
    else:
        # Admin de empresa vê apenas usuários da sua empresa
        users = CustomUser.objects.filter(
            company_obj=request.user.company_obj
        ).select_related("company_obj")
        companies = [request.user.company_obj] if request.user.company_obj else []

    # Roles disponíveis baseado no tipo de admin
    if request.user.is_instock_admin:
        role_choices = CustomUser.ROLE_CHOICES
    else:
        # Admin de empresa só pode criar gestores e operadores
        role_choices = [
            ("manager", "Gestor"),
            ("operator", "Operador"),
        ]

    context = {
        "users": users,
        "companies": companies,
        "role_choices": role_choices,
    }
    return render(request, "admin/users_management.html", context)


@login_required
def create_user_view(request):
    """View para criar um novo usuário"""
    if not request.user.can_manage_users():
        messages.error(request, "Você não tem permissão para criar usuários.")
        return redirect("dashboard")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        role_name = request.POST.get("role", "operator")
        company_id = request.POST.get("company")

        # Validações
        if not name or not email:
            messages.error(request, "Nome e email são obrigatórios.")
            return redirect("users_management")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Este email já está cadastrado.")
            return redirect("users_management")

        # Validação de papel - Admin de empresa não pode criar instock_admin ou company_admin
        if not request.user.is_instock_admin and role_name in [
            "instock_admin",
            "company_admin",
        ]:
            messages.error(
                request, "Você não tem permissão para criar este tipo de usuário."
            )
            return redirect("users_management")

        # Define a empresa
        if request.user.is_instock_admin and company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                company = None
        else:
            company = request.user.company_obj

        # Gera senha temporária
        temp_password = AccessRequest.generate_password()

        # Cria o usuário
        user = CustomUser.objects.create_user(
            email=email,
            password=temp_password,
            name=name,
            company_obj=company,
            company=company.name if company else None,
            role=role_name,
            must_change_password=True,
        )

        # Log de auditoria
        AuditService.log_create(request.user, user, request)

        messages.success(
            request, f"Usuário criado com sucesso! Senha temporária: {temp_password}"
        )
        return redirect("users_management")

    return redirect("users_management")


@login_required
def update_user_role_view(request, user_id):
    """View para atualizar o papel de um usuário"""
    if not request.user.can_manage_users():
        messages.error(request, "Você não tem permissão para editar usuários.")
        return redirect("dashboard")

    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
        return redirect("users_management")

    # Verifica se pode editar este usuário
    if (
        not request.user.is_instock_admin
        and target_user.company_obj != request.user.company_obj
    ):
        messages.error(request, "Você não pode editar usuários de outras empresas.")
        return redirect("users_management")

    if request.method == "POST":
        role_name = request.POST.get("role", "operator")

        # Validação de papel - Admin de empresa não pode promover para instock_admin ou company_admin
        if not request.user.is_instock_admin and role_name in [
            "instock_admin",
            "company_admin",
        ]:
            messages.error(request, "Você não tem permissão para atribuir este papel.")
            return redirect("users_management")

        # Captura valores antigos para auditoria
        old_values = {"role": target_user.role}

        # Atualiza o role
        target_user.role = role_name
        target_user.save()

        # Log de auditoria
        AuditService.log_update(
            request.user,
            target_user,
            old_values,
            request,
            changed_field="role",
            new_value=role_name,
        )

        messages.success(
            request,
            f"Papel do usuário atualizado para {dict(CustomUser.ROLE_CHOICES).get(role_name)}.",
        )

    return redirect("users_management")


@login_required
def toggle_user_status_view(request, user_id):
    """View para ativar/desativar um usuário"""
    if not request.user.can_manage_users():
        messages.error(request, "Você não tem permissão para editar usuários.")
        return redirect("dashboard")

    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
        return redirect("users_management")

    # Não pode desativar a si mesmo
    if target_user.id == request.user.id:
        messages.error(request, "Você não pode desativar sua própria conta.")
        return redirect("users_management")

    # Verifica se pode editar este usuário
    if (
        not request.user.is_instock_admin
        and target_user.company_obj != request.user.company_obj
    ):
        messages.error(request, "Você não pode editar usuários de outras empresas.")
        return redirect("users_management")

    # Alterna o status
    old_status = target_user.is_active if hasattr(target_user, "is_active") else True
    target_user.is_staff = (
        not target_user.is_staff
    )  # Usando is_staff como flag de ativo
    target_user.save()

    # Log de auditoria
    AuditService.log_update(
        request.user,
        target_user,
        {"is_active": old_status},
        request,
        changed_field="status",
    )

    status_msg = "ativado" if target_user.is_staff else "desativado"
    messages.success(request, f"Usuário {status_msg} com sucesso.")
    return redirect("users_management")


# ============================================
# VIEWS DE AUDITORIA
# ============================================


@login_required
def audit_logs_view(request):
    """View para visualizar logs de auditoria"""
    if not request.user.can_view_audit_logs():
        messages.error(request, "Você não tem permissão para ver os logs de auditoria.")
        return redirect("dashboard")

    # Filtros
    action_filter = request.GET.get("action", "")
    user_filter = request.GET.get("user", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # Query base
    if request.user.is_instock_admin:
        logs = AuditLog.objects.all()
    else:
        logs = AuditLog.objects.filter(company=request.user.company_obj)

    # Aplica filtros
    if action_filter:
        logs = logs.filter(action=action_filter)

    if user_filter:
        logs = logs.filter(user_email__icontains=user_filter)

    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)

    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)

    # Limita resultados e carrega relações
    logs = logs.select_related("user", "company", "content_type")[:200]

    context = {
        "logs": logs,
        "action_choices": AuditLog.ACTION_CHOICES,
        "filters": {
            "action": action_filter,
            "user": user_filter,
            "date_from": date_from,
            "date_to": date_to,
        },
    }
    return render(request, "admin/audit_logs.html", context)


# ============================================
# VIEWS DE EMPRESAS
# ============================================


@login_required
def companies_view(request):
    """View para listar empresas (apenas InStock admin)"""
    if not request.user.is_instock_admin:
        messages.error(
            request, "Apenas administradores InStock podem acessar esta página."
        )
        return redirect("dashboard")

    companies = Company.objects.all().prefetch_related("users", "products")

    context = {
        "companies": companies,
    }
    return render(request, "admin/companies.html", context)


@login_required
def company_detail_view(request, company_id):
    """View para detalhes de uma empresa"""
    if not request.user.is_instock_admin:
        # Permite ver apenas a própria empresa
        if str(request.user.company_obj.id) != str(company_id):
            messages.error(request, "Você não tem permissão para ver esta empresa.")
            return redirect("dashboard")

    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        messages.error(request, "Empresa não encontrada.")
        return redirect("companies")

    users = CustomUser.objects.filter(company_obj=company).select_related("role")
    products_count = company.products.count()
    sales_count = company.sales.count()
    suppliers_count = company.suppliers.count()
    recent_logs = AuditLog.objects.filter(company=company)[:20]

    context = {
        "company": company,
        "users": users,
        "products_count": products_count,
        "sales_count": sales_count,
        "suppliers_count": suppliers_count,
        "recent_logs": recent_logs,
    }
    return render(request, "admin/company_detail.html", context)


@login_required
def create_company_view(request):
    """View para criar uma nova empresa (apenas InStock admin)"""
    if not request.user.is_instock_admin:
        messages.error(request, "Apenas administradores InStock podem criar empresas.")
        return redirect("dashboard")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        cnpj = request.POST.get("cnpj", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not name or not cnpj:
            messages.error(request, "Nome e CNPJ são obrigatórios.")
            return redirect("companies")

        if Company.objects.filter(cnpj=cnpj).exists():
            messages.error(request, "Este CNPJ já está cadastrado.")
            return redirect("companies")

        company = Company.objects.create(
            name=name,
            cnpj=cnpj,
            email=email,
            phone=phone,
        )

        # Cria os roles padrão para a empresa
        for role_name in ["admin", "manager", "operator", "viewer"]:
            Role.create_for_company(company, role_name)

        # Log de auditoria
        AuditService.log_create(request.user, company, request)

        messages.success(request, f'Empresa "{name}" criada com sucesso!')
        return redirect("companies")

    return redirect("companies")
