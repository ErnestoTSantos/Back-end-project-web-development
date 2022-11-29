from django.db import models

from barbers.models import Barber


class Scheduling(models.Model):
    ACTION_STATES = (
        ("NCNF", "Not confirmed"),
        ("CONF", "Confirmed"),
        ("EXEC", "Executed"),
    )

    WORK_TYPES = (
        ("ND", "Selecionar"),
        ("CT", "Corte"),
        ("BB", "Barba"),
        ("PT", "Pintura"),
        ("CB", "Corte e Barba"),
        ("CP", "Corte e Pintura"),
        ("BP", "Barba e Pintura"),
    )

    provider = models.ForeignKey(
        Barber,
        related_name="barber",
        on_delete=models.CASCADE,
        verbose_name="Barbeiro",
        unique=False,
    )
    date_time = models.DateTimeField(verbose_name="Data e hora")
    client_name = models.CharField(verbose_name="Nome do cliente", max_length=200)
    client_phone = models.CharField(verbose_name="Número do cliente", max_length=20)
    state = models.CharField(
        verbose_name="status do horário",
        max_length=4,
        choices=ACTION_STATES,
        default="NCNF",
    )
    confirmed = models.BooleanField(verbose_name="Horário confirmado", default=False)
    work_type = models.CharField(
        verbose_name="Tipo de trabalho", choices=WORK_TYPES, default="ND", max_length=2
    )

    def __str__(self):
        return self.client_name
