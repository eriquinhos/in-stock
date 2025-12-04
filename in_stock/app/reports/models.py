from django.db import models


class Report(models.Model):
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="report_user",
        null=False,
    )
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
        verbose_name="Empresa"
    )
    TYPE_CHOICES = [
        ("expenses", "Despesas"),
        ("revenue", "Receitas"),
        ("full", "Completo"),
    ]
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, default="full")
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("id", "user")

    def __str__(self):
        return self.user + " gerou um relatório em " + self.date
