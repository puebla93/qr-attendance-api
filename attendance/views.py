from rest_framework import generics
from .models import *
from .serializers import *


class ListStudentsView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Students.objects.all()
    serializer_class = StudentsSerializer


class ListTeachersView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Teachers.objects.all()
    serializer_class = TeachersSerializer


class ListClassTypesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializer


class ListCoursesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Courses.objects.all()
    serializer_class = CoursesSerializer


class ListAttendancesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
