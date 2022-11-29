from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


class Barber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, blank=True, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_model",
        verbose_name="Usuário",
    )
    phone_number = models.CharField(verbose_name="Número de telefone", max_length=20)

    def __str__(self):
        return self.user.first_name
