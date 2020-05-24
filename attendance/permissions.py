from rest_framework.permissions import SAFE_METHODS, BasePermission


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
        return bool(request.user and request.user.is_teacher)


class IsStudentAssistantUser(BasePermission):
    """
        Allows access only to student assistant users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_student_assistant)

class IsOwner(BasePermission):
    """
        Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Access permissions are only allowed to the owner of the obj.
        return obj.owner == request.user
