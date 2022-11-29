from django.contrib import admin

from barbers.models import Barber


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number")

    def get_readonly_fields(self, request, obj):
        if obj:
            return [
                "id",
                "user",
                "phone_number",
            ]
        else:
            return ["id"]
