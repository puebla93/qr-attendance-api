from django.urls import path
from .views import ListAttendancesView


urlpatterns = [
    path('attendances/', ListAttendancesView.as_view(), name="attendances-all")
]
