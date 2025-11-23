from django.urls import path
from . import views

urlpatterns = [
    # Lista todos os relatórios (GET) e cria um novo relatório (POST)
    path("", views.ReportListCreateView.as_view(), name="report-list-create"),
]
