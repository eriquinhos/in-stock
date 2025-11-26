from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import CustomUserCreationForm
from .models import CustomUser
from .service import CustomUserService


class UserListCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    # Permitido acesso apenas para Admin ou SuperUsuário

    def test_func(self):
        # Retorna True se o usuário for permitido ou se tem permissão
        user = self.request.user
        if self.request.method == "POST":
            permission = ["users.add_customuser"]
        else:
            permission = ["users.view_customuser"]
        return (
            user.is_superuser
            or getattr(user, "type", None) == "admin"
            or user.has_perm(permission)
        )

    def get(self, request):

        # Lógica para listar todos os usuários

        users = CustomUserService.get_all()

        return render(request, "users/index.html", {"users": users})

    def post(self, request):
        # Lógica para criar um novo usuário
        # ... processar request.POST ...

        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "O usuário foi criado com sucesso!")
        else:
            messages.error(request, "Verifique os dados informados estão corretos.")

        return render(request, "users/create.html", {"form": form})


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    # Permitido acesso apenas para Admin ou SuperUsuário

    def test_func(self):
        # Retorna True se o usuário for permitido ou se tem permissão
        user = self.request.user

        if self.request.method == "GET" or self.request.method == "PUT":
            permission = ["users.change_customuser"]
        else:
            permission = ["users.delete_customuser"]
        return (
            user.is_superuser
            or getattr(user, "type", None) == "admin"
            or user.has_perm(permission)
        )

    # O Django irá redirecionar para a página 403 padrão (ou para 'permission_denied_url')
    # se test_func retornar False.

    def get(self, request, id_user):
        # Lógica para recuperar um usuário específico

        user = CustomUserService.get_user_by_id(id_user)

        if not user:
            return render(request, "errors/404.html")

        return render(request, "users/edit.html", {"user": user})

    def put(self, request, id_user):
        # Lógica para atualizar um usuário específico
        # ... processar request.body ...

        user = CustomUserService.get_user_by_id(id_user)

        if not user:
            return render(request, "errors/404.html")

        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            try:
                user_updated = CustomUserService.update_user(request, user)
                messages.success("O usuário foi atualizado com sucesso!")

            except Exception as e:
                messages.error(
                    "Não foi possível fazer a atualização do usuário devido a: {e}!"
                )
        else:
            messages.error("Os dados enviados não são válidos.")

        return (request, "users/edit.html", {"form": form})


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        # Retorna True se o usuário for permitido ou se tem permissão
        user = self.request.user
        if self.request.method == "POST":
            permission = ["users.add_customuser"]
        else:
            permission = ["users.view_customuser"]
        return (
            user.is_superuser
            or getattr(user, "type", None) == "admin"
            or user.has_perm(permission)
        )

    def post(self, request, id_user):
        # Lógica para deletar um usuário específico
        try:
            deleted = CustomUserService.delete_user_by_id(id_user)
        except Exception as e:
            messages.error(request, f"Erro ao excluir o usuário: {e}")
            return redirect("user-list-create")

        if not deleted:
            return render(request, "errors/404.html", status=404)

        messages.success(request, "O usuário foi deletado com sucesso!")
        return redirect("user-list-create")


class RegisterCreate(LoginRequiredMixin, UserPassesTestMixin, View):
    # Permitido acesso apenas para Admin ou SuperUsuário ou com permissão

    def test_func(self):
        user = self.request.user

        return (
            user.is_superuser
            or getattr(user, "type", None) == "admin"
            or user.has_perm("users.add_customuser")
        )

    def get(self, request):
        # Retornar a pagina do formulário
        form = CustomUserCreationForm()
        return render(request, "auth/register.html", {"form": form})

    def post(self, request):
        # Processa o formulário preenchido
        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():

            if CustomUser.objects.filter(email=request.POST.get("email")).exists():
                messages.error(request, "Este email já está em uso!")

            else:
                form.save()
                messages.success(request, "Usuário criado com sucesso!")

        else:
            messages.error(request, "Verifique os dados informados estão corretos.")

        return render(request, "auth/register.html", {"form": form})
