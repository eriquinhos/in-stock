from django.urls import path

from . import views

urlpatterns = [
    path("", views.SaleListView.as_view(), name="sale-list"),
    path("create/", views.SaleCreateView.as_view(), name="sale-create"),
]
