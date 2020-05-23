from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class ClassTypes(models.Model):
    # class type (eg. Practical Lesson, Conference)
    class_type = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.class_type

    @staticmethod
    def get_or_cretate_class_type(class_type):
        try:
            _class_type = ClassTypes.objects.get(class_type=class_type)
        except ClassTypes.DoesNotExist:
            _class_type = ClassTypes.objects.create(
                class_type=class_type
            )
        return _class_type


class Courses(models.Model):
    # course name (eg. Programming, Artificial Intelligence)
    course_name = models.CharField(max_length=255, null=False, unique=True)

    # course details (eg. Optative course, Elective course)
    course_details = models.TextField(default='')

    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.course_name


class Users(User):
    TEACHERS_EMAIL_ADDRESS = '@matcom.uh.cu'

    teaching = models.ManyToManyField(Courses, blank=True)

    @staticmethod
    def is_valid_teacher_email(teacher_email):
        return teacher_email.endswith(Users.TEACHERS_EMAIL_ADDRESS)

    @staticmethod
    def is_valid_student_id(student_id):
        from datetime import datetime

        birthday = student_id[:6]
        try:
            datetime(int("19"+birthday[:2]), int(birthday[2:4]), int(birthday[4:6]))
        except ValueError:
            try:
                datetime(int("20"+birthday[:2]), int(birthday[2:4]), int(birthday[4:6]))
            except ValueError:
                return False

        return True


class Attendances(models.Model):
    # the student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student')

    # the class teacher
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='teacher')

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
