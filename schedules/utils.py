from datetime import date, datetime, timedelta
from typing import List

import requests
from django.conf import settings


class ListingSchedules:
    @staticmethod
    def create_schedules(
        appointment_list: List, dt_start: datetime, dt_end: datetime, delta: timedelta
    ) -> List:
        while dt_start != dt_end:
            appointment_list.append({"date_time": dt_start})

            dt_start += delta

        return appointment_list

    @staticmethod
    def remove_scheduling_confirmed(appointment_list: List, serializer: List) -> List:
        for element in serializer:
            element = element.get("date_time")
            element_time = element[11:16]
            for time in appointment_list:
                date_time = time.get("date_time")
                time_appointment = datetime.strftime(date_time, "%H:%M")
                if time_appointment == element_time:
                    appointment_list.remove(time)

        return appointment_list


class Verifications:
    @staticmethod
    def is_holiday(date: date) -> bool:
        if settings.TESTING is True:
            if date.day == 25 and date.month == 12:
                return True
            return False

        api_request = "https://brasilapi.com.br/"
        request_api = requests.get(
            api_request + f"api/feriados/v1/{date.year}"
        )  # noqa:E501

        if request_api.status_code != 200:
            return False

        holidays = request_api.json()

        for holiday in holidays:
            date_holiday = holiday["date"]
            if datetime.strptime(date_holiday, "%Y-%m-%d").date() == date:
                return True

        return False

    @staticmethod
    def verification_weekday(appointment_list: List, date: date) -> List:
        dt_start = datetime(date.year, date.month, date.day, 9)
        dt_end_saturday = datetime(date.year, date.month, date.day, 13)
        dt_end = datetime(date.year, date.month, date.day, 18)
        delta = timedelta(minutes=30)

        if date.weekday() != 5 and date.weekday() != 6:
            ListingSchedules.create_schedules(appointment_list, dt_start, dt_end, delta)

        if date.weekday() == 5:
            ListingSchedules.create_schedules(
                appointment_list, dt_start, dt_end_saturday, delta
            )

        if date.weekday() == 6:
            # status 160 occurs when days is sunday
            appointment_list.append(
                {
                    "Information": "Infelizmente o barbeiro não trabalha aos domingos!",
                    "status": 160,
                }
            )

        return appointment_list
