from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings

from .models import *
from .serializers import *
from .permissions import *

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


class RegisterUsersView(generics.CreateAPIView):
    """
    POST auth/register/
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        if not username and not password and not email:
            return Response(
                data={
                    "message": "username, password and email is required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return Response(status=status.HTTP_201_CREATED)


class ListStudentsView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    permission_classes = (IsTeacherUser|IsStudentAssistantUser,)


class ListTeachersView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Teachers.objects.all()
    serializer_class = TeachersSerializer
    permission_classes = (IsTeacherUser,)


class ListClassTypesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializer
    permission_classes = (IsTeacherUser|IsStudentAssistantUser|ReadOnly,)


class ClassTypesDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        GET class_types/:id/
        PUT class_types/:id/
        DELETE class_types/:id/
    """

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializer

    def get(self, request, *args, **kwargs):
        try:
            class_type = self.queryset.get(class_type=kwargs["class_type"])
            return Response(ClassTypesSerializer(class_type).data)
        except ClassTypes.DoesNotExist:
            return Response(
                data={
                    "message": "ClassType with id: {} does not exist".format(kwargs["class_type"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        try:
            class_type = self.queryset.get(class_type=kwargs["class_type"])
            serializer = ClassTypesSerializer()
            updated_class_type = serializer.update(class_type, request.data)
            return Response(ClassTypesSerializer(updated_class_type).data)
        except ClassTypes.DoesNotExist:
            return Response(
                data={
                    "message": "ClassType with id: {} does not exist".format(kwargs["class_type"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            class_type = self.queryset.get(class_type=kwargs["class_type"])
            class_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClassTypes.DoesNotExist:
            return Response(
                data={
                    "message": "ClassType with id: {} does not exist".format(kwargs["class_type"])
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ListCoursesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Courses.objects.all()
    serializer_class = CoursesSerializer
    permission_classes = (IsTeacherUser|IsStudentAssistantUser|ReadOnly,)


class ListAttendancesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
    permission_classes = (permissions.IsAuthenticated,)
