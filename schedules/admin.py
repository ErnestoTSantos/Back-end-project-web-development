from django.contrib import admin

from schedules.models import Scheduling


@admin.register(Scheduling)
class AdminScheduling(admin.ModelAdmin):
    list_display = (
        "provider",
        "date_time",
        "client_name",
        "client_phone",
        "state",
        "work_type",
    )
