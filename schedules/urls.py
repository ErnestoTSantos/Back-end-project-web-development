from typing import Any, List

from django.contrib import admin
from django.urls import path

from schedules.views import ScheduleTime, ScheduleView, healthcheck

admin.site.site_header = "Time mapping admin :)!"

urlpatterns: List[Any] = [
    path("v1/", healthcheck, name="healthcheck"),
    path("v1/schedule-list/<str:date>/", ScheduleView.as_view()),
    path("v1/schedule-time/", ScheduleTime.as_view()),
]
