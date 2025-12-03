from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import get_template
from django.views import View
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings as django_settings
from datetime import timedelta
import secrets

import in_stock.config.settings as settings
from in_stock.app.pages.forms import LoginForm
from in_stock.app.products.models import Product, Category
from in_stock.app.suppliers.models import Supplier
from in_stock.app.sales.models import Sale
from in_stock.app.reports.models import Report
from in_stock.app.users.models import CustomUser, AccessRequest
from in_stock.app.users.forms import CustomUserCreationForm


def home(request):
    return render(request, "pages/index.html")


def dashboard_view(request):
    # Acesso apenas para autenticados
    if not request.user.is_authenticated:
        return render(request, "errors/401.html")
    
    # Verifica se precisa trocar a senha
    if request.user.must_change_password:
        return redirect("change_password")

    # Dados reais do banco de dados
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_sales = Sale.objects.count()
    total_reports = Report.objects.count()
    total_categories = Category.objects.count()
    
    # Calcular quantidade total de produtos em estoque
    total_stock = Product.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Vendas do mês atual
    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    sales_this_month = Sale.objects.filter(date__gte=first_day_of_month).count()
    
    # Entradas e saídas
    entries = Sale.objects.filter(type='entry').count()
    exits = Sale.objects.filter(type='exits').count()
    
    # Produtos com baixo estoque (menos de 10 unidades)
    low_stock_products = Product.objects.filter(quantity__lt=10).order_by('quantity')[:5]
    
    # Produtos próximos do vencimento (próximos 30 dias)
    thirty_days_from_now = today.date() + timedelta(days=30)
    expiring_soon = Product.objects.filter(
        expiration_date__lte=thirty_days_from_now,
        expiration_date__gte=today.date()
    ).order_by('expiration_date')[:5]
    
    # Últimas vendas/movimentações
    recent_sales = Sale.objects.select_related('product', 'user').order_by('-date')[:5]
    
    # Solicitações pendentes (apenas para admins InStock)
    pending_requests_count = 0
    pending_requests = []
    if request.user.is_instock_admin or request.user.is_superuser:
        pending_requests = AccessRequest.objects.filter(status='pending')
        pending_requests_count = pending_requests.count()

    context = {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_sales": total_sales,
        "total_reports": total_reports,
        "total_categories": total_categories,
        "total_stock": total_stock,
        "sales_this_month": sales_this_month,
        "entries": entries,
        "exits": exits,
        "low_stock_products": low_stock_products,
        "expiring_soon": expiring_soon,
        "recent_sales": recent_sales,
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
        if AccessRequest.objects.filter(personal_email=personal_email, status='pending').exists():
            messages.warning(request, "Já existe uma solicitação pendente com este email.")
            return render(request, self.template_name)

        # Verifica se já existe solicitação aprovada
        if AccessRequest.objects.filter(personal_email=personal_email, status='approved').exists():
            messages.warning(request, "Este email já possui uma conta aprovada. Tente fazer login.")
            return render(request, self.template_name)

        # Cria a solicitação
        AccessRequest.objects.create(
            name=name,
            personal_email=personal_email,
            company_name=company_name,
            cnpj=cnpj,
            phone=phone,
            message=message
        )

        messages.success(
            request,
            "Sua solicitação foi enviada com sucesso! Você receberá um email quando for aprovada."
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

    pending = AccessRequest.objects.filter(status='pending')
    approved = AccessRequest.objects.filter(status='approved').order_by('-updated_at')[:20]
    rejected = AccessRequest.objects.filter(status='rejected').order_by('-updated_at')[:20]

    context = {
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'pending_requests_count': pending.count(),
    }
    return render(request, "pages/access_requests.html", context)


@login_required
def approve_request_view(request, request_id):
    """Aprova uma solicitação de acesso"""
    if not (request.user.is_instock_admin or request.user.is_superuser):
        messages.error(request, "Você não tem permissão para aprovar solicitações.")
        return redirect("dashboard")

    access_request = get_object_or_404(AccessRequest, id=request_id)

    if access_request.status != 'pending':
        messages.warning(request, "Esta solicitação já foi processada.")
        return redirect("access_requests")

    # Gera email e senha
    generated_email = AccessRequest.generate_company_email(
        access_request.name, 
        access_request.company_name
    )
    generated_password = AccessRequest.generate_password()

    # Verifica se o email já existe e adiciona número se necessário
    base_email = generated_email
    counter = 1
    while CustomUser.objects.filter(email=generated_email).exists():
        parts = base_email.split('@')
        generated_email = f"{parts[0]}{counter}@{parts[1]}"
        counter += 1

    # Cria o usuário admin da empresa
    new_user = CustomUser.objects.create_user(
        email=generated_email,
        password=generated_password,
        name=access_request.name,
        company=access_request.company_name,
        type='admin',
        must_change_password=True
    )

    # Atualiza a solicitação
    access_request.status = 'approved'
    access_request.generated_email = generated_email
    access_request.generated_password = generated_password
    access_request.approved_by = request.user
    access_request.save()

    # Tenta enviar email
    try:
        send_mail(
            subject='InStock - Sua conta foi aprovada!',
            message=f'''
Olá {access_request.name},

Sua solicitação de acesso ao InStock foi aprovada!

Seus dados de acesso:
📧 Email: {generated_email}
🔑 Senha temporária: {generated_password}

Acesse: https://www.instock.app.br/login/

⚠️ No primeiro acesso, você será solicitado a alterar sua senha.

Atenciosamente,
Equipe InStock
            ''',
            from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'noreply@instock.app.br'),
            recipient_list=[access_request.personal_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

    messages.success(
        request,
        f"✅ Solicitação aprovada! Email: {generated_email} | Senha: {generated_password}"
    )
    return redirect("access_requests")


@login_required
def reject_request_view(request, request_id):
    """Rejeita uma solicitação de acesso"""
    if not (request.user.is_instock_admin or request.user.is_superuser):
        messages.error(request, "Você não tem permissão para rejeitar solicitações.")
        return redirect("dashboard")

    access_request = get_object_or_404(AccessRequest, id=request_id)

    if access_request.status != 'pending':
        messages.warning(request, "Esta solicitação já foi processada.")
        return redirect("access_requests")

    access_request.status = 'rejected'
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
