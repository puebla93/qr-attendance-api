from django.db import models
from django.contrib.auth.models import User


class Users(User):
    TEACHERS_EMAIL_ADDRESS = '@matcom.uh.cu'

    # Read about user permissions
    # role = models.CharField()

    @staticmethod
    def is_valid_teacher_email(teacher_email):
        return teacher_email.endswith(Users.TEACHERS_EMAIL_ADDRESS)

    @staticmethod
    def is_valid_student_id(student_id):
        from datetime import datetime
        try:
            datetime(int("19"+student_id[:2]), int(student_id[2:4]), int(student_id[4:6]))
        except ValueError:
            try:
                datetime(int("20"+student_id[:2]), int(student_id[2:4]), int(student_id[4:6]))
            except ValueError:
                return False

        return True

class ClassTypes(models.Model):
    # class type (eg. Practical Lesson, Conference)
    class_type = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.class_type


class Courses(models.Model):
    # course name (eg. Programming, Artificial Intelligence)
    course_name = models.CharField(max_length=255, null=False, unique=True)

    # course details (eg. Optative course, Elective course)
    course_details = models.TextField(default='')

    def __str__(self):
        return self.course_name


class Attendances(models.Model):
    # the student
    student = models.ForeignKey(Users, on_delete=models.CASCADE)

    # the class teacher
    teacher = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='teacher')

    # class date
    date = models.DateField(editable=False)

    # course (eg. Programming, Artificial Intelligence)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)

    # class type (eg. Practical Lesson, Conference)
    class_type = models.ForeignKey(ClassTypes, on_delete=models.DO_NOTHING)

    # class details (eg. Last Practical Lesson, First Conference)
    details =  models.TextField(default='')

    def __str__(self):
        return "{} - {}:{} - {}".format(self.student, self.class_type, self.course, self.date)
