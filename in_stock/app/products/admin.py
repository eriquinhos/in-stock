from django.contrib import admin
from in_stock.app.products.models import Product, Category

admin.site.register(Product)
admin.site.register(Category)
