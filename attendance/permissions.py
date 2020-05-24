from rest_framework.permissions import SAFE_METHODS, BasePermission
from .models import *


class ReadOnly(BasePermission):
    """
        Allows access only to read-only request.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsTeacherUser(BasePermission):
    """
        Allows access only to teacher users.
    """

    def has_permission(self, request, view):
        return bool(request.user and Users.is_valid_teacher_email(request.user.username))


class IsStudentAssistantUser(BasePermission):
    """
        Allows access only to student assistant users.
    """

    def has_permission(self, request, view):
        course_name = request.data.get("course_name", "")
        try:
            course = Courses.objects.get(course_name=course_name)
        except Courses.DoesNotExist:
            return False
        return bool(request.user and request.user in course.teachers.all())


class IsOwner(BasePermission):
    """
        Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Access permissions are only allowed to the owner of the obj.
        return obj.student == request.user
