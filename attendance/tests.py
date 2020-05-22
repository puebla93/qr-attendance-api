import datetime
import json
import random

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from .models import *
from .serializers import *
from .util import is_valid_student_id, is_valid_teacher_email

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
        if is_valid_student_id(student_id) and student_name != "":
            first_name = student_name.split()[0]
            last_name = student_name.split()[1:]
            return User.objects.create(
                username=student_id,
                password=student_id,
                first_name=first_name,
                last_name=last_name
            )

    @staticmethod
    def create_teacher(teacher_email="", teacher_name=""):
        if is_valid_teacher_email(teacher_email) and teacher_name != "":
            first_name = teacher_name.split()[0]
            last_name = teacher_name.split()[1:]
            return User.objects.create(
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


class ClassTypesViewTest(BaseViewTest):
    """
        Tests for the class_types/ endpoints
    """

    CLASS_TYPES = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]

    def setUp(self):
        super(ClassTypesViewTest, self).setUp()

        # add test data
        [self.create_class_type(ClassTypesViewTest.CLASS_TYPES[i]) for i in range(4)]

    def fetch_a_class_type(self, class_type):
        return self.client.get(
            reverse(
                "class_types-detail",
                kwargs={
                    "version": "v1",
                    "type": class_type
                }
            )
        )

    def update_a_class_type(self, class_type, data):
        """
            Make a put request to update a class_type
            :return:
        """

        return self.client.put(
            reverse(
                "class_types-detail",
                kwargs={
                    "version": "v1",
                    "type": class_type
                }
            ),
            data=json.dumps(data),
            content_type='application/json'
        )

    def delete_a_class_type(self, class_type):
        return self.client.delete(
            reverse(
                "class_types-detail",
                kwargs={
                    "version": "v1",
                    "type": class_type
                }
            )
        )

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

    def test_get_a_class_type_that_does_not_exist(self):
        """
        This test try to get a class type that doesn't exists and make assertions
        """

        # test with a class type that does not exist
        response = self.fetch_a_class_type("Invalid class type")
        self.assertEqual(
            response.data["message"],
            "ClassType: \"Invalid class type\" does not exist"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_a_class_type(self):
        """
            This test ensures that a single class type of a given type is
            returned
        """

        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.fetch_a_class_type(class_type)
        # fetch the data from db
        expected = ClassTypes.objects.get(class_type=class_type)
        serialized = ClassTypesSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_a_class_type_no_logged_user(self):
        """
            This test ensures that to update a class_type the user need to be logged
        """

        # hit the API endpoint no logged user
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        new_class_type = "New class type no logged user"
        response = self.update_a_class_type(
            class_type=class_type,
            data={"class_type": new_class_type}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_a_class_type_no_teacher_user(self):
        """
            This test ensures that a no teacher user can't update a class_type
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint unauthorized user
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        new_class_type = "New class type unauthorized user"
        response = self.update_a_class_type(
            class_type=class_type,
            data={"class_type": new_class_type}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_a_class_type_that_does_not_exist(self):
        """
            This test try to update a class type that doesn't exists and make assertions
        """

        self.login_client(self.admin.username, 'testing')

        # test with invalid data
        class_type = "Class type doesn't exist"
        response = self.update_a_class_type(
            class_type=class_type,
            data={"class_type": "Any Value"}
        )
        self.assertEqual(
            response.data["message"],
            "ClassType: {} does not exist".format(class_type)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_a_class_type(self):
        """
            This test ensures that a single class_type can be updated
        """

        self.login_client(self.admin.username, 'testing')

        # hit the API endpoint valid user
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        new_class_type = "New class type"
        response = self.update_a_class_type(
            class_type=class_type,
            data={"class_type": new_class_type}
        )
        self.assertEqual(response.data, {"class_type": new_class_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_a_class_type_no_logged_user(self):
        """
            This test ensures that to delete a class_type the user need to be logged
        """

        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.delete_a_class_type(class_type)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_a_class_type_no_teacher_user(self):
        """
            This test ensures that a no teacher user can't delete a class_type
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.delete_a_class_type(class_type)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_a_class_type_that_does_not_exist(self):
        """
            This test try to delet a class type that doesn't exists and make assertions
        """

        self.login_client(self.admin.username, 'testing')

        # test with invalid data
        class_type = "Class type doesn't exist"
        response = self.delete_a_class_type(class_type)
        self.assertEqual(
            response.data["message"],
            "ClassType: {} does not exist".format(class_type)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_a_class_type(self):
        """
            This test ensures that a class_type of given type can be deleted
        """

        self.login_client(self.admin.username, 'testing')
        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.delete_a_class_type(class_type)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


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
        user = User.objects.get(username="new_user@mail.com")
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
                    "password": "",
                    "email": ""
                }
            ),
            content_type='application/json'
        )
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
