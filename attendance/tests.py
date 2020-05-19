import datetime
import random

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from .models import *
from .serializers import *

# tests for views


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def get_random_student_ids(k):
        start_date = datetime.date(1990, 1, 1)
        end_date = datetime.date(2020, 1, 1)

        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days

        ids = []
        for _ in range(k):
            random_number_of_days = random.randrange(days_between_dates)
            random_date = start_date + datetime.timedelta(days=random_number_of_days)
            ids.append(str(random_date.year % 100)+str(random_date.month)+str(random_date.day))

        return ids

    @staticmethod
    def create_student(student_id="", student_name=""):
        if Students.valid_id(student_id) and student_name != "":
            return Students.objects.create(id=student_id, name=student_name)

    @staticmethod
    def create_teacher(teacher_name=""):
        if teacher_name != "":
            return Teachers.objects.create(name=teacher_name)

    @staticmethod
    def create_class_type(class_type=""):
        if class_type != "":
            return ClassTypes.objects.create(class_type=class_type)

    @staticmethod
    def create_course(course_name=""):
        if course_name != "":
            return Courses.objects.create(course_name=course_name)

    @staticmethod
    def create_attendance(
            student=None, teacher=None, date=None, course=None, class_type=None, details=""):
        if student and teacher and date and course and class_type and details != "":
            return Attendances.objects.create(student=student, teacher=teacher, date=date,
                                              course=course, class_type=class_type, details=details)


class GetAllStudentsTest(BaseViewTest):

    def setUp(self):
        # add test data
        ids = BaseViewTest.get_random_student_ids(4)
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        [self.create_student(ids[i], names[i]) for i in range(4)]

    def test_get_all_students(self):
        """
            This test ensures that all students added in the setUp method
            exist when we make a GET request to the students/ endpoint
        """

        # hit the API endpoint
        response = self.client.get(
            reverse("students-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Students.objects.all()
        serialized = StudentsSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllTeachersTest(BaseViewTest):

    def setUp(self):
        # add test data
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        [self.create_teacher(names[i]) for i in range(4)]

    def test_get_all_teachers(self):
        """
            This test ensures that all teachers added in the setUp method
            exist when we make a GET request to the teachers/ endpoint
        """

        # hit the API endpoint
        response = self.client.get(
            reverse("teachers-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Teachers.objects.all()
        serialized = TeachersSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllClassTypesTest(BaseViewTest):

    def setUp(self):
        # add test data
        class_types = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]
        [self.create_class_type(class_types[i]) for i in range(4)]

    def test_get_all_class_types(self):
        """
            This test ensures that all class_types added in the setUp method
            exist when we make a GET request to the class_types/ endpoint
        """

        # hit the API endpoint
        response = self.client.get(
            reverse("class_types-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = ClassTypes.objects.all()
        serialized = ClassTypesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllCoursesTest(BaseViewTest):

    def setUp(self):
        # add test data
        course_names = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]
        [self.create_course(course_names[i]) for i in range(4)]

    def test_get_all_courses(self):
        """
            This test ensures that all courses added in the setUp method
            exist when we make a GET request to the courses/ endpoint
        """

        # hit the API endpoint
        response = self.client.get(
            reverse("courses-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Courses.objects.all()
        serialized = CoursesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllAttendancesTest(BaseViewTest):

    def setUp(self):
        # add test data
        ids = BaseViewTest.get_random_student_ids(4)
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        students = [self.create_student(ids[i], names[i]) for i in range(4)]
        teachers = [self.create_teacher(names[i]) for i in range(4)]

        course_names = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]
        courses = [self.create_course(course_names[i]) for i in range(4)]

        class_types = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]
        class_types = [self.create_class_type(class_types[i]) for i in range(4)]

        dates = [datetime.datetime.now() - datetime.timedelta(days=days) for days in range(4)]
        details = ["", "Lesson Before Final Test", "Last Practical Lesson", "First Conference"]
        [self.create_attendance(students[i], teachers[i], dates[i], courses[i],
                                class_types[i], details[i]) for i in range(4)]

    def test_get_all_attendances(self):
        """
            This test ensures that all attendances added in the setUp method
            exist when we make a GET request to the attendances/ endpoint
        """

        # hit the API endpoint
        response = self.client.get(
            reverse("attendances-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Attendances.objects.all()
        serialized = AttendancesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
