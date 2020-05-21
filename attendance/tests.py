import datetime
import json
import random

from django.contrib.auth.models import User
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
            year = str(random_date.year)[2:]
            month = '0'+str(random_date.month) if random_date.month < 10 else str(random_date.month)
            day = '0'+str(random_date.day) if random_date.day < 10 else str(random_date.day)
            ids.append(year + month + day)

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

    def login_client(self, username="", password=""):
        # get a token from DRF
        response = self.client.post(
            reverse('create-token'),
            data=json.dumps(
                {
                    'username': username,
                    'password': password
                }
            ),
            content_type='application/json'
        )
        self.token = response.data['token']
        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    def setUp(self):
        # create an admin user
        self.admin = User.objects.create_superuser(
            username="jonny",
            email="jonny@email.com",
            password="testing",
            first_name="John",
            last_name="Doe",
        )
        # create a regular user
        self.user = User.objects.create_user(
            username="jane",
            email="jane@email.com",
            password="testing",
            first_name="Jane",
            last_name="Doe",
        )


class GetAllStudentsTest(BaseViewTest):
    """
        Tests for the students/ endpoint
    """

    def setUp(self):
        super(GetAllStudentsTest, self).setUp()

        # add test data
        ids = BaseViewTest.get_random_student_ids(4)
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        for i in range(4):
            self.create_student(ids[i], names[i])

    def test_get_all_students(self):
        """
            This test ensures that all students added in the setUp method
            exist when we make a GET request to the students/ endpoint
        """

        self.login_client(self.admin.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("students-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Students.objects.all()
        serialized = StudentsSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_students_bad_user(self):
        """
            This test ensures that a non admin user can't access to the 
            students/ endpoint
        """

        self.login_client(self.user.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("students-all", kwargs={"version": "v1"})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetAllTeachersTest(BaseViewTest):
    """
        Tests for the teachers/ endpoint
    """

    def setUp(self):
        super(GetAllTeachersTest, self).setUp()

        # add test data
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        [self.create_teacher(names[i]) for i in range(4)]

    def test_get_all_teachers(self):
        """
            This test ensures that all teachers added in the setUp method
            exist when we make a GET request to the teachers/ endpoint
        """

        self.login_client(self.admin.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("teachers-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Teachers.objects.all()
        serialized = TeachersSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_teachers_bad_user(self):
        """
            This test ensures that a non admin user can't access to the 
            teachers/ endpoint
        """

        self.login_client(self.user.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("teachers-all", kwargs={"version": "v1"})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetAllClassTypesTest(BaseViewTest):
    """
        Tests for the class_types/ endpoint
    """

    def setUp(self):
        super(GetAllClassTypesTest, self).setUp()

        # add test data
        class_types = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]
        [self.create_class_type(class_types[i]) for i in range(4)]

    def test_get_all_class_types(self):
        """
            This test ensures that all class_types added in the setUp method
            exist when we make a GET request to the class_types/ endpoint
        """

        self.login_client(self.admin.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("class_types-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = ClassTypes.objects.all()
        serialized = ClassTypesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_class_types_bad_user(self):
        """
            This test ensures that a non admin user can't access to the 
            class_types/ endpoint
        """

        self.login_client(self.user.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("class_types-all", kwargs={"version": "v1"})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetAllCoursesTest(BaseViewTest):
    """
        Tests for the courses/ endpoint
    """

    def setUp(self):
        super(GetAllCoursesTest, self).setUp()

        # add test data
        course_names = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]
        [self.create_course(course_names[i]) for i in range(4)]

    def test_get_all_courses(self):
        """
            This test ensures that all courses added in the setUp method
            exist when we make a GET request to the courses/ endpoint
        """

        self.login_client(self.admin.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("courses-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Courses.objects.all()
        serialized = CoursesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_courses_bad_user(self):
        """
            This test ensures that a non admin user can't access to the 
            courses/ endpoint
        """

        self.login_client(self.user.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("courses-all", kwargs={"version": "v1"})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetAllAttendancesTest(BaseViewTest):
    """
        Tests for the attendances/ endpoint
    """

    def setUp(self):
        super(GetAllAttendancesTest, self).setUp()

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

        self.login_client(self.user.username, "testing")

        # hit the API endpoint
        response = self.client.get(
            reverse("attendances-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Attendances.objects.all()
        serialized = AttendancesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthLoginUserTest(BaseViewTest):
    """
        Tests for the auth/login/ endpoint
    """

    def login_a_user(self, username="", password=""):
        url = reverse(
            "auth-login",
            kwargs={
                "version": "v1"
            }
        )
        return self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type="application/json"
        )

    def test_login_user_with_valid_credentials(self):
        # test login with valid credentials
        response = self.login_a_user(self.user.username, "testing")
        # assert token key exists
        self.assertIn("token", response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_with_invalid_credentials(self):
        # test login with invalid credentials
        response = self.login_a_user("anonymous", "pass")
        # assert status code is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
