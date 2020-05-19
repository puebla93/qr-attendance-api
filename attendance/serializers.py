from rest_framework import serializers

from .models import *


class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = ("id", "name")


class TeachersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = ("name",)


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
