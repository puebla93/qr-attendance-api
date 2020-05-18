from rest_framework import serializers
from .models import Attendances


class AttendancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendances
        fields = ("id", "name", "teacher", "course_name", "class_type", "date", "details")
