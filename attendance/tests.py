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
        if Users.is_valid_student_id(student_id) and student_name != "":
            first_name = student_name.split()[0]
            last_name = student_name.split()[1:]
            return Users.objects.create(
                username=student_id,
                password=student_id,
                first_name=first_name,
                last_name=last_name
            )

    @staticmethod
    def create_teacher(teacher_email="", teacher_name=""):
        if Users.is_valid_teacher_email(teacher_email) and teacher_name != "":
            first_name = teacher_name.split()[0]
            last_name = teacher_name.split()[1:]
            return Users.objects.create(
                username=teacher_email,
                email=teacher_email,
                password="password",
                first_name=first_name,
                last_name=last_name
            )

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
        url = reverse(
            "auth-login",
            kwargs={
                "version": "v1"
            }
        )
        # get a token
        response = self.client.post(
            url,
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
    """
        Tests for the attendances/ endpoint
    """

    def setUp(self):
        super(GetAllAttendancesTest, self).setUp()

        # add test data
        ids = BaseViewTest.get_random_student_ids(4)
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        students = [self.create_student(ids[i], names[i]) for i in range(4)]

        emails = [name.lower().split()[0]+"."+name.lower().split()[1]+"@matcom.uh.cu" for name in names]
        teachers = [self.create_teacher(emails[i], names[i]) for i in range(4)]

        course_names = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]
        courses = [self.create_course(course_name) for course_name in course_names]

        class_types = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]
        class_types = [self.create_class_type(class_type) for class_type in class_types]

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


class AuthRegisterUserTest(BaseViewTest):
    """
        Tests for auth/register/ endpoint
    """

    def test_register_a_user_with_valid_data(self):
        url = reverse(
            "auth-register",
            kwargs={
                "version": "v1"
            }
        )
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "username": "new_user",
                    "password": "new_pass",
                    "email": "new_user@mail.com",
                    "first_name": "New",
                    "last_name": "User"
                }
            ),
            content_type="application/json"
        )
        # assert status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="new_user")
        self.assertEqual(user.email, "new_user@mail.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")

    def test_register_a_user_with_invalid_data(self):
        url = reverse(
            "auth-register",
            kwargs={
                "version": "v1"
            }
        )
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "username": "",
                    "password": "",
                    "email": ""
                }
            ),
            content_type='application/json'
        )
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
