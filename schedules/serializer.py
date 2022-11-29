import re
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import serializers

from barbers.models import Barber
from schedules.models import Scheduling


class SchedulingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduling
        fields = [
            "id",
            "provider",
            "date_time",
            "client_name",
            "client_phone",
            "state",
            "work_type",
        ]

    provider = serializers.CharField()
    work_type = serializers.CharField()

    def get_hour(self, value, hour, minutes):
        date = datetime(value.year, value.month, value.day, hour, minutes)
        return date.strftime("%H:%M")

    def validate_provider(self, provider):
        try:
            provider_obj = Barber.objects.get(user__first_name=provider)
        except Barber.DoesNotExist:
            raise serializers.ValidationError("Barbeiro não existe!")

        return provider_obj

    def validate_date_time(self, date):
        if date < timezone.now():
            raise serializers.ValidationError(
                "O agendamento não pode ser realizado no passado!"
            )

        if date and datetime.date(date).weekday() == 6:
            raise serializers.ValidationError(
                "Infelizmente o barbeiro não trabalha aos domingos!"
            )

        if date:
            time = datetime.strftime(date, "%H:%M")

            lunch_time = self.get_hour(date, 12, 0)

            return_interval = self.get_hour(date, 13, 0)

            open_time = self.get_hour(date, 9, 0)

            closing_time = self.get_hour(date, 18, 0)

            if datetime.date(date).weekday() == 5 and time >= return_interval:
                raise serializers.ValidationError(
                    "Infelizmente o profissional só trabalha até as 13h no sábado!"
                )
            elif (
                return_interval > time >= lunch_time
                and datetime.date(date).weekday() != 5
            ):
                raise serializers.ValidationError(
                    "O barbeiro está no horário de almoço!"
                )
            elif open_time > time:
                raise serializers.ValidationError("O barbeiro abre apenas às 9h!")
            elif closing_time <= time:
                raise serializers.ValidationError("O barbeiro encerra às 18h!")

        qs = Scheduling.objects.filter(confirmed=True)

        delta = timedelta(minutes=30)

        if qs:
            for element in qs:
                date_element = datetime.date(element.date_time)
                date_request = datetime.date(date)

                if date_element == date_request:
                    if (
                        element.date_time + delta <= date
                        or date + delta <= element.date_time
                    ):
                        pass
                    else:
                        raise serializers.ValidationError(
                            "Infelizmente o horário selecionado está indisponível!"
                        )

        return date

    def validate_client_name(self, client_name):
        amount_characters_name = len(client_name)

        if amount_characters_name < 6:
            raise serializers.ValidationError(
                "O nome do cliente precisa ter 6 ou mais caracteres!"
            )

        if not " " in client_name:  # noqa:E713
            raise serializers.ValidationError("O cliente precisa ter um sobrenome!")

        return client_name

    def validate_client_phone(self, phone_number):
        verification_numbers = re.sub(r"[^0-9+() -]", "", phone_number)
        amount_characters_phone = len(phone_number)

        if not phone_number.startswith("+") and not phone_number.startswith("+55"):
            raise serializers.ValidationError("O número deve começar com '(+55)'")

        if phone_number and amount_characters_phone < 12:
            raise serializers.ValidationError(
                "O número de telefone precisa ter no mínimo 8 digitos!"
            )

        if phone_number != verification_numbers:
            raise serializers.ValidationError(
                "O número pode ter apenas valores entre 0-9, parenteses, traços, espaço e o sinal de mais!"
            )

        return phone_number

    def validate_work_type(self, work_type):
        WORK_TYPES = [
            "Corte",
            "Barba",
            "Pintura",
            "Corte e Barba",
            "Corte e Pintura",
            "Barba e Pintura",
        ]

        work_db = [
            "CT",
            "BB",
            "PT",
            "CB",
            "CP",
            "BP",
        ]

        if work_type == "":
            raise serializers.ValidationError(
                "É necessário passar um tipo de trabalho!"
            )

        if work_type not in WORK_TYPES:
            raise serializers.ValidationError(
                "Tipo de trabalho inexistente, por favor selecione uma opção válida"
            )

        work = WORK_TYPES.index(work_type)
        work_type = work_db[work]

        return work_type

    def validate(self, data):
        provider = data.get("provider")
        client_name = data.get("client_name")
        date_time = data.get("date_time")
        client_phone = data.get("client_phone")
        state = data.get("state")

        if state:
            scheduling = Scheduling.objects.filter(
                client_name=client_name,
                client_phone=client_phone,
                state="NCNF",
                date_time=date_time,
            ).first()
            if scheduling:
                scheduling.state = "CONF"
                scheduling.confirmed = True
                scheduling.save()
                data["state"] = "CONF"
            else:
                raise serializers.ValidationError("O horário não pode ser confirmado!")

        if date_time and client_phone:
            if Scheduling.objects.filter(
                provider__user__first_name=provider,
                client_phone=client_phone,
                date_time__date=date_time,
            ).exists():
                raise serializers.ValidationError(
                    "O(A) cliente não pode ter duas reservas no mesmo dia!"
                )
        elif client_name and client_phone and date_time:
            if Scheduling.objects.filter(
                provider__user__first_name=provider,
                date_time=date_time,
                client_name=client_name,
                client_phone=client_phone,
            ).exists():
                raise serializers.ValidationError(
                    "O(A) cliente não pode ter duas reservas no mesmo dia!"
                )

        if client_phone.startswith("+") and not client_phone.startswith("+55"):
            raise serializers.ValidationError(
                "Deve estar associado a um número do Brasil (+55)"
            )

        return data
