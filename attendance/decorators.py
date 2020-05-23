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
                    "message": "class_type are required to create a class type"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated