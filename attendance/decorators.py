from rest_framework.response import Response
from rest_framework.views import status
from .models import Users


def validate_attendance_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        student_id = args[0].request.data.get("student_id", "")
        student_name = args[0].request.data.get("student_name", "")
        course_name = args[0].request.data.get("course_name", "")
        class_type = args[0].request.data.get("class_type", "")
        date = args[0].request.data.get("date", "")
        if not (student_id and student_name and course_name and class_type and date):
            return Response(
                data={
                    "message": "student_id, student_name, course_name, class_type and date are required to add an attendance"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not Users.is_valid_student_id(student_id):
            return Response(
                data={
                    "message": "student_id is invalid"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_class_type_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        class_type = args[0].request.data.get("class_type", "")
        if not class_type:
            return Response(
                data={
                    "message": "class_type is required to create/update a class type"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated

def validate_course_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        course_name = args[0].request.data.get("course_name", "")
        if not course_name:
            return Response(
                data={
                    "message": "course_name is required to create/update a course"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        teachers = args[0].request.data.get("teachers", [])
        if isinstance(teachers, list):
            for teacher in teachers:
                try:
                    user = Users.objects.get(username=teacher)
                    if not Users.is_valid_student_id(user.username):
                        return Response(
                            data={
                                "message": "user with username: {} isn't a student".format(teacher)
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Users.DoesNotExist:
                    return Response(
                        data={
                            "message": "user with username: {} does't exists".format(teacher)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(
                data={
                    "message": "teachers must be a list"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated
