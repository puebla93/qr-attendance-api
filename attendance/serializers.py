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
    teachers = serializers.SlugRelatedField(many=True, queryset=Users.objects.all(), slug_field='username')

    class Meta:
        model = Courses
        fields = ("course_name", "course_details", "teachers")

    def update(self, instance, validated_data):
        instance.course_name = validated_data["course_name"]
        instance.course_details = validated_data.get("course_details", "")
        teachers = validated_data.get("teachers", [])
        teachers = [Users.objects.get(username=teacher) for teacher in teachers]
        instance.teachers.set(teachers)
        return instance


class UsersSerializer(serializers.ModelSerializer):
    full_name = serializers.StringRelatedField(source="get_full_name")
    teaching = serializers.StringRelatedField(many=True)

    class Meta:
        model = Users
        fields = ("username", "full_name", "teaching")


class AttendancesSerializer(serializers.ModelSerializer):
    student_id = serializers.StringRelatedField(source='student')
    student_name = serializers.StringRelatedField(source="student.get_full_name")
    teacher_name = serializers.StringRelatedField(source="teacher.get_full_name")
    course_name = serializers.StringRelatedField(source='course')
    class_type = serializers.StringRelatedField()

    class Meta:
        model = Attendances
        fields = ("student_id", "student_name", "teacher_name", "date", "course_name", "class_type", "details")
