from .models import CustomUser


class CustomUserService():
    def get_all(self):
        return CustomUser.objects.all()

    def create_user(self, request):
        pass

    def get_user_by_id(self, id_user: int):
        try:
            user = CustomUser.objects.get(pk=id_user)
            return user
        except CustomUser.DoesNotExist:
            return False

    def update_user(self, request, user: CustomUser):

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            raise Exception("As senhas não coincidem!")

        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone') or None
        user.type = request.POST.get('type')

        # Criptografa a senha
        user.set_password(password1)

        user.save()
        return user

    def delete_user_by_id(self, id_user: int):
        try:
            user = CustomUser.objects.get(pk=id_user)
            user.delete()
            return True

        except CustomUser.DoesNotExist:
            return False

        except Exception:
            # Deixa view decidir o que fazer
            raise
