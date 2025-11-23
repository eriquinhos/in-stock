from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.template.loader import get_template
import in_stock.config.settings as settings
from django.contrib.auth import authenticate, login, logout
from in_stock.app.pages.forms import LoginForm
from django.contrib import messages


def home(request):
    return render(request, "pages/index.html")


def dashboard_view(request):
    # Acesso apenas para autenticados
    if not request.user.is_authenticated:
        return render(request, "errors/401.html")

    context = {
        "total_products": 120,
        "total_suppliers": 15,
        "total_sales": 80,
        "total_reports": 5,
    }
    return render(request, "pages/dashboard.html", context)


class LoginCreateView(View):
    template_name = "auth/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
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
