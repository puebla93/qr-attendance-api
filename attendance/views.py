from rest_framework import generics
from .models import Attendances
from .serializers import AttendancesSerializer


class ListAttendancesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
