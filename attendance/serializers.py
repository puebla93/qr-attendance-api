from rest_framework import serializers

from .models import *
from .relations import *


class TokenSerializer(serializers.Serializer):
    """
        This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)


class ClassTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTypes
        fields = ("class_type",)


class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ("course_name", "course_details")


class AttendancesSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(source='student.username')
    student_name = FunctionRelatedField(source='student', func_name="get_full_name")
    teacher_name = FunctionRelatedField(source='teacher', func_name="get_full_name")
    course_name = serializers.StringRelatedField(source='course')
    class_type = serializers.StringRelatedField()

    class Meta:
        model = Attendances
        fields = ("student_id", "student_name", "teacher_name", "date", "course_name", "class_type", "details")
