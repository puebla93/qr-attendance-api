from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class ClassTypes(models.Model):
    # class type (eg. Practical Lesson, Conference)
    class_type = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.class_type

    @classmethod
    def get_or_cretate_class_type(cls, class_type):
        try:
            _class_type = cls.objects.get(class_type=class_type)
        except cls.DoesNotExist:
            _class_type = cls.objects.create(
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

    @classmethod
    def get_or_cretate_course(cls, course_name, course_details="", teachers=[]):
        try:
            course = cls.objects.get(course_name=course_name)
        except cls.DoesNotExist:
            teachers = [Users.objects.get(username=teacher) for teacher in teachers]
            course = cls.objects.create(
                course_name=course_name,
                course_details=course_details,
            )
            course.teachers.set(teachers)
        return course


class Users(User):
    TEACHERS_EMAIL_ADDRESS = '@matcom.uh.cu'
    STUDENT_ID_LENGTH = 11

    teaching = models.ManyToManyField(Courses, blank=True)

    @classmethod
    def is_valid_teacher_email(cls, teacher_email):
        return teacher_email.endswith(cls.TEACHERS_EMAIL_ADDRESS)

    @classmethod
    def is_valid_student_id(cls, student_id):
        from datetime import date

        if len(student_id) != cls.STUDENT_ID_LENGTH:
            return False

        birthday = student_id[:6]
        try:
            date(int("19"+birthday[:2]), int(birthday[2:4]), int(birthday[4:6]))
        except ValueError:
            try:
                date(int("20"+birthday[:2]), int(birthday[2:4]), int(birthday[4:6]))
            except ValueError:
                return False

        return True

    @classmethod
    def get_or_create_student(cls, student_id, student_name):
        if not cls.is_valid_student_id(student_id):
            return None
        try:
            student_user = cls.objects.get(username=student_id)
        except cls.DoesNotExist:
            first_name = student_name[0]
            last_name = student_name[1]
            student_user = cls.objects.create(
                username=student_id,
                password=student_id,
                first_name=first_name,
                last_name=last_name
            )
        return student_user


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
