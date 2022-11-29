import re

from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, ValidationError

from barbers.models import Barber


class BarberSerializer(ModelSerializer):
    class Meta:
        model = Barber
        fields = ["id", "user", "phone_number"]

    def validate_phone_number(self, phone_number):
        if phone_number.startswith("+") and phone_number.startswith("+55"):
            verification_numbers = re.sub(r"[^0-9+() -]", "", phone_number)
            amount_characters_phone = len(phone_number)

            if phone_number and amount_characters_phone < 12:
                raise ValidationError(
                    "O número de telefone precisa ter no mínimo 8 digitos!"
                )

            if phone_number != verification_numbers:
                raise ValidationError(
                    "O número pode ter apenas valores entre 0-9, parenteses, traços, espaço e o sinal de mais!"
                )

        else:
            raise ValidationError("O número deve começar com '(+55)'.")


class UserSerialzier(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "user_model"]

    def validate_username(self, username):
        user = User.objects.filter(username=username).first()

        if user:
            raise ValidationError(f"O username {username}, já está em uso!")

        if username == "":
            raise ValidationError("É necessário passar um nome de usuário!")

        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 3:
            raise ValidationError("O primeiro nome precisa ter no mínimo 3 caracteres!")

        if " " in first_name:
            raise ValidationError("O primeiro nome não pode ter espaço!")

        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 6:
            raise ValidationError("O último nome precisa ter no mínimo 6 caracteres!")

        if " " in last_name:
            raise ValidationError("O último nome não pode ter espaço!")

        return last_name

    def validate(self, data):
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")

        if username and first_name and last_name:
            user = User.objects.update(
                username=username, first_name=first_name, last_name=last_name
            )
        elif username and first_name:
            user = User.objects.update(username=username, first_name=first_name)
        elif username and last_name:
            user = User.objects.update(username=username, last_name=last_name)
        elif first_name and last_name:
            user = User.objects.update(first_name=first_name, last_name=last_name)
        elif username:
            user = User.objects.update(username=username)
        elif first_name:
            user = User.objects.update(first_name=first_name)
        elif last_name:
            user = User.objects.update(last_name=last_name)
        else:
            raise ValidationError(
                "Alguma informação precisa ser passada para a atualização!"
            )

        return user
