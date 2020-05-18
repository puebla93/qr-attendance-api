from django.db import models


class Students(models.Model):
    # student id
    id = models.CharField(max_length=255, null=False, primary_key=True)

    # student name
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "N:{} CI:{}".format(self.name, self.id)


class Teachers(models.Model):
    # teacher name
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class ClassTypes(models.Model):
    # class type (eg. Practical Lesson, Conference)
    class_type = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.class_type


class Courses(models.Model):
    # course name (eg. Programming, Artificial Intelligence)
    course_name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.course_name


class Attendances(models.Model):
    # the student
    student = models.ForeignKey(Students)

    # the class teacher
    teacher = models.ForeignKey(Teachers)

    # class date
    date = models.DateField(editable=False)

    # course name (eg. Programming, Artificial Intelligence)
    course_name = models.ForeignKey(ClassTypes)

    # class type (eg. Practical Lesson, Conference)
    class_type = models.ForeignKey(ClassTypes)

    # class details (eg. Last Practical Lesson, First Conference)
    details = models.CharField(max_length=255, null=True)

    def __str__(self):
        return "{} - {}:{} - {}".format(self.student, self.class_type, self.course_name, self.date)
