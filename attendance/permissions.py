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

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Attendances):
            course = obj.course
        else:
            course = obj
        return request.user in course.teachers.all()


class IsAssistanceOwner(BasePermission):
    """
        Allows access only to the student assistances.
    """

    def has_object_permission(self, request, view, obj):
        return obj.student == request.user
