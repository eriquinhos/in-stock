from django.contrib import admin

from in_stock.app.products.models import Category, Product

admin.site.register(Product)
admin.site.register(Category)
