from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings

from .models import *
from .serializers import *

# Get the JWT settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class LoginView(generics.CreateAPIView):
    """
        POST auth/login/
    """

    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )})
            serializer.is_valid()
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ListStudentsView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    permission_classes = (permissions.IsAdminUser,)


class ListTeachersView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Teachers.objects.all()
    serializer_class = TeachersSerializer
    permission_classes = (permissions.IsAdminUser,)


class ListClassTypesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializer
    permission_classes = (permissions.IsAdminUser,)


class ListCoursesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Courses.objects.all()
    serializer_class = CoursesSerializer
    permission_classes = (permissions.IsAdminUser,)


class ListAttendancesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
    permission_classes = (permissions.IsAuthenticated,)
