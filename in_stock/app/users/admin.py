from django.contrib import admin

from in_stock.app.users.models import CustomUser

admin.site.register(CustomUser)
