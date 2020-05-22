from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings

from .models import *
from .serializers import *
from .permissions import *
from .decorators import *

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
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        if not (email and password):
            return Response(
                data={
                    "message": "email and password is required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return Response(status=status.HTTP_201_CREATED)


class ListClassTypesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializer


class ClassTypesDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        GET class_types/:type/
        PUT class_types/:type/
        DELETE class_types/:type/
    """

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializer
    permission_classes = (permissions.IsAdminUser|ReadOnly,)

    def get(self, request, *args, **kwargs):
        try:
            class_type = self.queryset.get(class_type=kwargs["type"])
            return Response(ClassTypesSerializer(class_type).data)
        except ClassTypes.DoesNotExist:
            return Response(
                data={
                    "message": "ClassType: \"{}\" does not exist".format(kwargs["type"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        try:
            class_type = self.queryset.get(class_type=kwargs["type"])
            serializer = ClassTypesSerializer()
            updated_class_type = serializer.update(class_type, request.data)
            return Response(ClassTypesSerializer(updated_class_type).data)
        except ClassTypes.DoesNotExist:
            return Response(
                data={
                    "message": "ClassType: {} does not exist".format(kwargs["type"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            class_type = self.queryset.get(class_type=kwargs["type"])
            class_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClassTypes.DoesNotExist:
            return Response(
                data={
                    "message": "ClassType: {} does not exist".format(kwargs["type"])
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ListCoursesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Courses.objects.all()
    serializer_class = CoursesSerializer


class CoursesDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        GET courses/:name/
        PUT courses/:name/
        DELETE courses/:name/
    """

    queryset = Courses.objects.all()
    serializer_class = CoursesSerializer
    permission_classes = (IsTeacherUser|ReadOnly,)

    def get(self, request, *args, **kwargs):
        try:
            course = self.queryset.get(course_name=kwargs["name"])
            return Response(CoursesSerializer(course).data)
        except Courses.DoesNotExist:
            return Response(
                data={
                    "message": "Course with name: {} does not exist".format(kwargs["name"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        try:
            course = self.queryset.get(course_name=kwargs["name"])
            serializer = CoursesSerializer()
            updated_course = serializer.update(course, request.data)
            return Response(CoursesSerializer(updated_course).data)
        except Courses.DoesNotExist:
            return Response(
                data={
                    "message": "Course with name: {} does not exist".format(kwargs["name"])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            course = self.queryset.get(course_name=kwargs["name"])
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Courses.DoesNotExist:
            return Response(
                data={
                    "message": "Course with name: {} does not exist".format(kwargs["name"])
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ListAttendancesView(generics.ListAPIView):
    """
        Provides a get method handler.
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CreateAttendancesView(generics.CreateAPIView):
    """
        POST attendances/
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
    permission_classes = (IsTeacherUser|IsStudentAssistantUser,)

    @validate_attendance_request_data
    def post(self, request, *args, **kwargs):
        student_id = request.data["student_id"]
        student_name = request.data["student_name"]
        student = self.get_or_create_student(student_id, student_name)

        teacher = None

        course_name = request.data["course_name"]
        course = self.get_or_cretate_course(course_name)
        class_type = request.data["class_type"]
        class_type = self.get_or_cretate_class_type(class_type)

        date = request.data["date"]
        details = request.data.get("details", "")

        attendance = Attendances.objects.create(
            student=student,
            teacher=teacher,
            course=course,
            class_type=class_type,
            date=date,
            details=details
        )
        return Response(
            data=AttendancesSerializer(attendance).data,
            status=status.HTTP_201_CREATED
        )


class AttendancesDetailView(generics.RetrieveAPIView):
    """
        GET attendances/:id/
    """

    queryset = Attendances.objects.all()
    serializer_class = AttendancesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            attendance = self.queryset.get(id=kwargs["id"])
            return Response(AttendancesSerializer(attendance).data)
        except Attendances.DoesNotExist:
            return Response(
                data={
                    "message": "Attendance with id: {} does not exist".format(kwargs["id"])
                },
                status=status.HTTP_404_NOT_FOUND
            )
