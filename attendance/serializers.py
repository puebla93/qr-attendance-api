from rest_framework import serializers

from .models import *


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
        fields = ("course_name",)


class AttendancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendances
        fields = ("student", "teacher", "date", "course", "class_type", "details")
