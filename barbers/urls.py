from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    token_obtain_pair,
)

from barbers.views import (
    BarberCreateView,
    BarberDetailView,
    BarberListingTimesView,
    BarberUpdateSchedulingStatusView,
    get_ref_user,
    healthckeck,
)

app_name = "barbers"

urlpatterns = [
    # Rotas para utilização
    path("v1/", healthckeck),
    path("v1/loggin/", token_obtain_pair),
    path("v1/refresh-loggin/", TokenRefreshView.as_view(), name="token_refresh"),
    path("v1/create-user/", BarberCreateView.as_view()),
    path("v1/list-times-provider/", BarberListingTimesView.as_view()),
    path("v1/barber-updates/<str:uuid>/", BarberDetailView.as_view()),
    path("v1/get-barber-id/", get_ref_user),
    path(
        "v1/confirm-scheduling/<str:uuid>/", BarberUpdateSchedulingStatusView.as_view()
    ),
    # Token
    path("v1/token/loggin/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
