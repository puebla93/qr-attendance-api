from django.db import models


class Attendances(models.Model):
    # student id
    student_id = models.CharField(max_length=255, null=False)

    # student name
    student_name = models.CharField(max_length=255, null=False)

    # teacher name
    teacher = models.CharField(max_length=255, null=False)

    # class date
    date = models.DateField(editable=False)

    # course name (eg. Programming, Artificial Intelligence)
    course_name = models.CharField(max_length=255, null=False)

    # class type (eg. Practical Lesson, Conference)
    class_type = models.CharField(max_length=255, null=False)

    # class details (eg. Last Practical Lesson, First Conference)
    details = models.CharField(max_length=255, null=True)

    def __str__(self):
        return "{} - {}:{} - {}".format(self.student_name, self.class_type, self.course_name, self.date)
