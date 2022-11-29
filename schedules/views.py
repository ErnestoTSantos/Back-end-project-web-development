from datetime import datetime

from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from barbers.models import Barber
from schedules.models import Scheduling
from schedules.serializer import SchedulingSerializer
from schedules.utils import ListingSchedules, Verifications


class ScheduleView(APIView):
    def get(self, request, date):
        date = datetime.strptime(date, "%Y-%m-%d").date()
        provider = request.query_params.get("provider", None)
        provider = Barber.objects.filter(user__first_name=provider).first()
        appointment_list = []

        holiday = Verifications.is_holiday(date)

        if holiday:
            # status 150 occurs when the date is a holiday.
            appointment_list.append(
                {"Information": "A data selecionada é um feriado!", "status": 150}
            )
            return JsonResponse(appointment_list, safe=False)

        if not provider:
            # status 151 occurs when barber isn't found
            return Response(
                {
                    "Information": "Infelizmente nenhum barbeiro foi encontrado, tente novamente!",
                    "status": 151,
                }
            )

        qs = Scheduling.objects.filter(
            date_time__date=date, state="CONF", confirmed=True
        ).order_by("date_time__time")
        serializer = SchedulingSerializer(qs, many=True)

        appointment_list = Verifications.verification_weekday(appointment_list, date)

        schedule_list = ListingSchedules.remove_scheduling_confirmed(
            appointment_list, serializer.data
        )

        return JsonResponse(schedule_list, safe=False)


class ScheduleTime(ListCreateAPIView):
    serializer_class = SchedulingSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        date_time = data.get("date_time")
        work_type = data.get("work_type")
        date = datetime.strptime(date_time[:10], "%Y-%m-%d").date()

        holiday = Verifications.is_holiday(date)

        if holiday:
            raise serializers.ValidationError(
                "Infelizmente agendamentos não podem ser realizados em feriados!"
            )

        # if not work_type:
        #     raise serializers.ValidationError(
        #         "É necessário passar um tipo de trabalho!"
        #     )

        return super().post(request, *args, **kwargs)


@api_view(http_method_names=["GET"])
def healthcheck(request):
    return Response({"status": "OK"}, status=200)
