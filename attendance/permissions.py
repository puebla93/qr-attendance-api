from rest_framework.permissions import SAFE_METHODS, BasePermission
from .models import *


class ReadOnly(BasePermission):
    """
        Allows access only to read-only request.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        False


class IsTeacherUser(BasePermission):
    """
        Allows access only to teacher users.
    """

    def has_permission(self, request, view):
        return bool(request.user and Users.is_valid_teacher_email(request.user.username))


class IsCourseTeacher(BasePermission):
    """
        Allows access only to teachers of a course.
    """

    def has_object_permission(self, request, view, course):
        return bool(request.user and request.user in course.teachers.all())


class IsStudentAssistantUser(BasePermission):
    """
        Allows access only to student assistant users.
    """

    def has_permission(self, request, view):
        return bool(request.user and Users(request.user).is_student_assistant_user)


class IsOwner(BasePermission):
    """
        Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Access permissions are only allowed to the owner of the obj.
        return obj.student == request.user
