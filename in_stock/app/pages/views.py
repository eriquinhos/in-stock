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
from in_stock.app.users.forms import CustomUserCreationForm
from in_stock.app.users.models import AccessRequest, CustomUser, PasswordResetToken


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
    if request.user.is_instock_admin or request.user.is_superuser:
        pending_requests = AccessRequest.objects.filter(status="pending")
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
    """View pública para solicitar acesso (admins de empresas)"""

    template_name = "auth/request_access.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")

        name = request.POST.get("name", "").strip()
        personal_email = request.POST.get("personal_email", "").strip()
        company_name = request.POST.get("company_name", "").strip()
        cnpj = request.POST.get("cnpj", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        # Validações
        if not all([name, personal_email, company_name, cnpj]):
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
            return render(request, self.template_name)

        # Verifica se já existe solicitação pendente
        if AccessRequest.objects.filter(
            personal_email=personal_email, status="pending"
        ).exists():
            messages.warning(
                request, "Já existe uma solicitação pendente com este email."
            )
            return render(request, self.template_name)

        # Verifica se já existe solicitação aprovada
        if AccessRequest.objects.filter(
            personal_email=personal_email, status="approved"
        ).exists():
            messages.warning(
                request, "Este email já possui uma conta aprovada. Tente fazer login."
            )
            return render(request, self.template_name)

        # Cria a solicitação
        AccessRequest.objects.create(
            name=name,
            personal_email=personal_email,
            company_name=company_name,
            cnpj=cnpj,
            phone=phone,
            message=message,
        )

        messages.success(
            request,
            "Sua solicitação foi enviada com sucesso! Você receberá um email quando for aprovada.",
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
    """Lista todas as solicitações de acesso (apenas admins InStock)"""
    if not (request.user.is_instock_admin or request.user.is_superuser):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("dashboard")

    pending = AccessRequest.objects.filter(status="pending")
    approved = AccessRequest.objects.filter(status="approved").order_by("-updated_at")[
        :20
    ]
    rejected = AccessRequest.objects.filter(status="rejected").order_by("-updated_at")[
        :20
    ]

    context = {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "pending_requests_count": pending.count(),
    }
    return render(request, "pages/access_requests.html", context)


@login_required
def approve_request_view(request, request_id):
    """Aprova uma solicitação de acesso"""
    if not (request.user.is_instock_admin or request.user.is_superuser):
        messages.error(request, "Você não tem permissão para aprovar solicitações.")
        return redirect("dashboard")

    access_request = get_object_or_404(AccessRequest, id=request_id)

    if access_request.status != "pending":
        messages.warning(request, "Esta solicitação já foi processada.")
        return redirect("access_requests")

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
        type="admin",
        must_change_password=True,
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

    messages.success(
        request,
        f"✅ Solicitação aprovada! Email: {generated_email} | Senha: {generated_password}",
    )
    return redirect("access_requests")


@login_required
def reject_request_view(request, request_id):
    """Rejeita uma solicitação de acesso"""
    if not (request.user.is_instock_admin or request.user.is_superuser):
        messages.error(request, "Você não tem permissão para rejeitar solicitações.")
        return redirect("dashboard")

    access_request = get_object_or_404(AccessRequest, id=request_id)

    if access_request.status != "pending":
        messages.warning(request, "Esta solicitação já foi processada.")
        return redirect("access_requests")

    access_request.status = "rejected"
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
