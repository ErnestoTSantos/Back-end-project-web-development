import re

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from barbers.models import Barber
from barbers.serializer import BarberSerializer, UserSerialzier
from schedules.models import Scheduling
from schedules.serializer import SchedulingSerializer


class BarberListingTimesView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        username = request.query_params.get("username")

        user = User.objects.filter(username=username).first()

        if user:
            barber = Barber.objects.filter(user=user).first()
            if barber:
                qs = Scheduling.objects.filter(provider=barber)
                scheduling_serializer = SchedulingSerializer(qs, many=True)
                return Response(data={"scheduling_list": scheduling_serializer.data})
        return Response(data={"error": "User not found!"}, status=400)


class BarberDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "uuid"

    def get_object(self):
        self.kwargs["uuid"]
        return super().get_object()

    def get_serializer_class(self, element, data=None, serializer_type=None):
        if self.request.method == "PUT":
            if serializer_type == "barber":
                serializer = BarberSerializer(element, partial=True, data=data)
                if serializer.is_valid():
                    serializer = [serializer.data]
                    return serializer
                else:
                    return serializer.errors
            else:
                serializer = UserSerialzier(element, partial=True, data=data)
                if serializer.is_valid():
                    serializer = [serializer.data]
                    return serializer
                else:
                    return serializer.errors
        else:
            if serializer_type == "barber":
                serializer = BarberSerializer(element)
                return serializer.data
            else:
                serializer = UserSerialzier(element)
                return serializer.data

    def get_queryset(self, data=None, serializer_type=None):
        uuid = self.kwargs.get("uuid")
        barber = Barber.objects.filter(id=uuid).first()
        user = User.objects.filter(username=barber.user).first()
        if self.request.method == "PUT":
            if serializer_type == "barber":
                barber = self.get_serializer_class(barber, data, "barber")
                return barber
            else:
                user = self.get_serializer_class(user, data)
                return user
        else:
            barber = self.get_serializer_class(barber, serializer_type="barber")
            user = self.get_serializer_class(user)

            return barber, user

    def put(self, request, *args, **kwargs):
        data = request.data
        phone_number = data.get("phone_number")

        if phone_number:
            qs = self.get_queryset(data, "barber")
        else:
            qs = self.get_queryset(data)

        return Response(data={"user_update": qs}, status=200)

    def get(self, request, *args, **kwargs):
        barber, user = self.get_queryset()

        barber_id = barber.get("id")
        barber_phone = barber.get("phone_number")
        user_id = user.get("id")
        username = user.get("username")
        first_name = user.get("first_name")
        last_name = user.get("last_name")

        informations = {
            "id": user_id,
            "ref": barber_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": barber_phone,
        }

        qs = [informations]

        return Response(data={"informations": qs})


class BarberUpdateSchedulingStatusView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "uuid"

    def get_object(self):
        self.kwargs["uuid"]
        return super().get_object()

    def get_queryset(self, barber_id, client_name, client_phone, date_time):
        barber = Barber.objects.filter(id=barber_id).first()

        scheduling = Scheduling.objects.filter(
            provider=barber,
            client_name=client_name,
            client_phone=client_phone,
            date_time=date_time,
        ).first()
        return scheduling

    def get_serializer_class(self, scheduling, data):
        serializer = SchedulingSerializer(scheduling, data=data, partial=True)
        if serializer.is_valid():
            return serializer.data
        else:
            serializer.errors

    def put(self, request, *args, **kwargs):
        data = request.data
        data["state"] = "CONF"

        client_name = data.get("client_name")
        client_phone = data.get("client_phone")
        date_time = data.get("date_time")
        uuid = self.kwargs.get("uuid")

        qs = self.get_queryset(
            barber_id=uuid,
            client_name=client_name,
            client_phone=client_phone,
            date_time=date_time,
        )

        serializer = self.get_serializer_class(scheduling=qs, data=data)

        return Response(data={"information": serializer})


class BarberCreateView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get("username")
        password = data.get("password")
        confirmation_password = data.get("confirmation_password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        phone_number = data.get("phone_number")

        user = None

        if username == first_name and username == last_name:
            raise serializers.ValidationError(
                "O nome de usuário não pode ser igual ao primeiro nome, ou o último nome!"
            )

        if first_name == last_name:
            raise serializers.ValidationError(
                "O primeiro e o último nome não podem ser iguais!"
            )

        if phone_number:
            if phone_number.startswith("+") and phone_number.startswith("+55"):
                verification_numbers = re.sub(r"[^0-9+() -]", "", phone_number)
                amount_characters_phone = len(phone_number)

                if phone_number and amount_characters_phone < 12:
                    raise serializers.ValidationError(
                        "O número de telefone precisa ter no mínimo 8 digitos!"
                    )

                if phone_number != verification_numbers:
                    raise serializers.ValidationError(
                        "O número pode ter apenas valores entre 0-9, parenteses, traços, espaço e o sinal de mais!"
                    )

            else:
                raise serializers.ValidationError("O número deve começar com '(+55)'.")
        else:
            raise serializers.ValidationError("O número não pode ser vazio!")

        if (
            password != ""
            and confirmation_password != ""
            and password == confirmation_password
        ):
            if username and first_name and last_name:
                user = User.objects.create(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=False,
                )
            else:
                raise serializers.ValidationError(
                    "Verifique se o campo username, first name e last name está preenchido!"
                )
        else:
            raise serializers.ValidationError("As senhas não são coincidentes!")

        if user:
            Barber.objects.create(user=user, phone_number=phone_number)

        return Response(data={"user_created": True})


@api_view(http_method_names=["GET"])
@permission_classes(IsAuthenticated)
def get_ref_user(request):
    username = request.query_params.get("username")

    if username:
        barber = Barber.objects.filter(user__username=username).first()
        return Response(data={"user_ref": barber.id}, status=200)
    else:
        return Response(data={"information": "Usuário não informado!"}, status=400)


@api_view(http_method_names=["GET"])
def healthckeck(request):
    return Response({"status": "OK"}, status=200)
