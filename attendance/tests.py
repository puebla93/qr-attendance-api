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
            remaining = str(random.randrange(99999))
            ids.append(year + month + day + remaining)

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
        if student and teacher and date and course and class_type:
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

    def make_request(self, url_name, kind="get", data=None, **kwargs):
        """
            Make a request to url_name endpoint
        :param kind: HTTP VERB
        :return:
        """

        kwargs.update({"version": "v1"})
        if kind == "get":
            return self.client.get(
                reverse(
                    url_name,
                    kwargs=kwargs
                )
            )
        elif kind == "post":
            return self.client.post(
                reverse(
                   url_name,
                    kwargs=kwargs
                ),
                data=json.dumps(data),
                content_type='application/json'
            )
        elif kind == "put":
            return self.client.put(
                reverse(
                    url_name,
                    kwargs=kwargs
                ),
                data=json.dumps(data),
                content_type='application/json'
            )
        elif kind == "delete":
            return self.client.delete(
                reverse(
                   url_name,
                    kwargs=kwargs
                )
            )
        else:
            return None


class ClassTypesViewTest(BaseViewTest):
    """
        Tests for the class_types/ endpoints
    """

    CLASS_TYPES = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]

    def setUp(self):
        super(ClassTypesViewTest, self).setUp()

        # add test data
        [self.create_class_type(ClassTypesViewTest.CLASS_TYPES[i]) for i in range(4)]

    def test_get_all_class_types(self):
        """
            This test ensures that all class_types added in the setUp method
            exist when we make a GET request to the class_types/ endpoint
        """

        # hit the API endpoint
        response = self.make_request("class_types-all")
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
        class_type = "Invalid class type"
        response = self.make_request("class_types-detail", type=class_type)
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
        response = self.make_request("class_types-detail", type=class_type)
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
        response = self.make_request("class_types-detail", kind="put",
            data={"class_type": new_class_type},
            type=class_type
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_a_class_type_no_teacher_user(self):
        """
            This test ensures that a not teacher user can't update a class_type
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint unauthorized user
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        new_class_type = "New class type unauthorized user"
        response = self.make_request("class_types-detail", kind="put",
            data={"class_type": new_class_type},
            type=class_type
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_a_class_type_that_does_not_exist(self):
        """
            This test try to update a class type that doesn't exists and make assertions
        """

        self.login_client(self.admin.username, 'testing')

        # test with invalid data
        class_type = "Class type doesn't exist"
        response = self.make_request("class_types-detail", kind="put",
            data={"class_type": "Any Value"},
            type=class_type
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
        response = self.make_request("class_types-detail", kind="put",
            data={"class_type": new_class_type},
            type=class_type
        )
        self.assertEqual(response.data, {"class_type": new_class_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_a_class_type_no_logged_user(self):
        """
            This test ensures that to delete a class_type the user need to be logged
        """

        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.make_request("class_types-detail", kind="delete",
            type=class_type
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_a_class_type_no_teacher_user(self):
        """
            This test ensures that a not teacher user can't delete a class_type
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.make_request("class_types-detail", kind="delete",
            type=class_type
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_a_class_type_that_does_not_exist(self):
        """
            This test try to delet a class type that doesn't exists and make assertions
        """

        self.login_client(self.admin.username, 'testing')

        # test with invalid data
        class_type = "Class type doesn't exist"
        response = self.make_request("class_types-detail", kind="delete",
            type=class_type
        )
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
        response = self.make_request("class_types-detail", kind="delete",
            type=class_type
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CoursesViewTest(BaseViewTest):
    """
        Tests for the courses/ endpoints
    """

    COURSE_NAMES = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]

    def setUp(self):
        super(CoursesViewTest, self).setUp()

        # add test data
        [self.create_course(CoursesViewTest.COURSE_NAMES[i]) for i in range(4)]

    def test_get_all_courses(self):
        """
            This test ensures that all courses added in the setUp method
            exist when we make a GET request to the courses/ endpoint
        """

        # hit the API endpoint
        response = self.make_request("courses-all")
        # fetch the data from db
        expected = Courses.objects.all()
        serialized = CoursesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_a_course_that_does_not_exist(self):
        """
            This test try to get a course that doesn't exists and make assertions
        """

        # test with a course that does not exist
        course = "Invalid course"
        response = self.make_request("courses-detail", name=course)
        self.assertEqual(
            response.data["message"],
            "Course with name: \"Invalid course\" does not exist"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_a_course(self):
        """
            This test ensures that a single course of a given type is
            returned
        """

        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        response = self.make_request("courses-detail", name=course_name)
        # fetch the data from db
        expected = Courses.objects.get(course_name=course_name)
        serialized = CoursesSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_a_course_no_logged_user(self):
        """
            This test ensures that to update a course the user need to be logged
        """

        # hit the API endpoint no logged user
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        new_course_name = "New course no logged user"
        response = self.make_request("courses-detail", kind="put",
            data={"course_name": new_course_name},
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_a_course_no_teacher_user(self):
        """
            This test ensures that a not teacher user can't update a course
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint unauthorized user
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        new_course_name = "New course unauthorized user"
        response = self.make_request("courses-detail", kind="put",
            data={"course_name": new_course_name},
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_a_course_that_does_not_exist(self):
        """
            This test try to update a course that doesn't exists and make assertions
        """

        self.login_client(self.admin.username, 'testing')

        # test with invalid data
        course_name = "Course doesn't exist"
        response = self.make_request("courses-detail", kind="put",
            data={"course_name": "Any Value"},
            name=course_name
        )
        self.assertEqual(
            response.data["message"],
            "Course with name: \"{}\" does not exist".format(course_name)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_a_course(self):
        """
            This test ensures that a single course can be updated
        """

        self.login_client(self.admin.username, 'testing')

        # hit the API endpoint valid user
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        new_course_name = "New course"
        response = self.make_request("courses-detail", kind="put",
            data={"course_name": new_course_name},
            name=course_name
        )
        self.assertEqual(response.data, {"course_name": new_course_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_a_course_no_logged_user(self):
        """
            This test ensures that to delete a course the user need to be logged
        """

        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        response = self.make_request("courses-detail", kind="delete",
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_a_course_no_teacher_user(self):
        """
            This test ensures that a no teacher user can't delete a course
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        response = self.make_request("courses-detail", kind="delete",
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_a_course_that_does_not_exist(self):
        """
            This test try to delet a course that doesn't exists and make assertions
        """

        self.login_client(self.admin.username, 'testing')

        # test with invalid data
        course_name = "Course doesn't exist"
        response = self.make_request("courses-detail", kind="delete",
            name=course_name
        )
        self.assertEqual(
            response.data["message"],
            "Course with name: \"{}\" does not exist".format(course_name)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_a_course(self):
        """
            This test ensures that a course of given type can be deleted
        """

        self.login_client(self.admin.username, 'testing')
        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        response = self.make_request("courses-detail", kind="delete",
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AttendancesViewTest(BaseViewTest):
    """
        Tests for the attendances/ endpoint
    """

    def setUp(self):
        super(AttendancesViewTest, self).setUp()

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

    def create_attendance_data(self, create_objects=True):
        student_id = BaseViewTest.get_random_student_ids(1)[0]
        student_name = "Matcom Student"
        teacher_name = "Matcom Teacher"
        teacher_email = "matcom.teacher@matcom.uh.cu"
        course_name = "Operating System"
        class_type = "Partial Exam"
        date = datetime.datetime.now()
        iso_date = datetime.datetime.isoformat(date)

        if create_objects:
            self.create_student(student_id, student_name)
            self.create_teacher(teacher_name, teacher_email)
            self.create_course(course_name)
            self.create_class_type(class_type)

        return {
            "student_id": student_id,
            "student_name": student_name,
            "course_name": course_name,
            "class_type": class_type,
            "date": iso_date
        }

    def test_get_all_attendances_no_logged_user(self):
        """
            This test ensures that to get all attendances the user need to be logged
        """

        # hit the API endpoint no logged user
        response = self.make_request("attendances-list-create")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_all_attendances(self):
        """
            This test ensures that all attendances added in the setUp method
            exist when we make a GET request to the attendances/ endpoint
        """

        self.login_client(self.user.username, "testing")

        # hit the API endpoint
        response = self.make_request("attendances-list-create")
        # fetch the data from db
        expected = Attendances.objects.all()
        serialized = AttendancesSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_an_attendance_no_logged_user(self):
        """
            This test ensures that to get an attendance the user need to be logged
        """

        # hit the API endpoint no logged user
        attendance = random.randint(1, 4)
        response = self.make_request("attendances-detail", id=attendance)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_an_attendance_that_does_not_exist(self):
        """
            This test try to get an attendances that doesn't exists and make assertions
        """

        self.login_client(self.user.username, 'testing')

        # test with a attendance that does not exist
        attendance = 5
        response = self.make_request("attendances-detail", id=attendance)
        self.assertEqual(
            response.data["message"],
            "Attendance with id: {} does not exist".format(attendance)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_an_attendance(self):
        """
            This test ensures that a single attendance of a given type is
            returned
        """

        self.login_client(self.user.username, 'testing')

        # hit the API endpoint
        attendance = random.randint(1, 4)
        response = self.make_request("attendances-detail", id=attendance)
        # fetch the data from db
        expected = Attendances.objects.get(id=attendance)
        serialized = AttendancesSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_an_attendance_no_logged_user(self):
        """
            This test ensures that to create an attendance the user need to be logged
        """

        attendance = self.create_attendance_data()

        # hit the API endpoint
        response = self.make_request("attendances-list-create", kind="post", data=attendance)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_an_attendance_no_authorized_user(self):
        """
            This test ensures that an unauthorized user can't create an attendance
        """

        self.login_client(self.user.username, 'testing')

        attendance = self.create_attendance_data()

        # hit the API endpoint
        response = self.make_request("attendances-list-create", kind="post", data=attendance)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_an_invalid_attendance(self):
        """
            This test ensures that a single attendance can't be added with invalid data
        """

        self.login_client(self.admin.username, 'testing')

        invalid_attendance = {}

        # test with invalid data
        response = self.make_request("attendances-list-create", kind="post", data=invalid_attendance)
        self.assertEqual(
            response.data["message"],
            "student_id, student_name, course_name, class_type and date are required to add an attendance"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_an_attendance(self):
    #     """
    #         This test ensures that a single attendance can be added
    #     """

    #     self.login_client(self.admin.username, 'testing')

    #     # hit the API endpoint
    #     attendance = self.create_attendance_data(create_objects=False)
    #     response = self.make_request("attendances-list-create", kind="post", data=attendance)

    #     self.assertEqual(response.data, attendance)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthLoginUserTest(BaseViewTest):
    """
        Tests for the auth/login/ endpoint
    """

    def test_login_user_with_invalid_credentials(self):
        """
            Test login user with invalid credentials
        """

        user_data = {
            "username": "anonymous",
            "password": "pass"
        }
        response = self.make_request("auth-login", kind="post", data=user_data)
        # assert status code is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_user(self):
        """
            Test login user with valid credentials
        """

        user_data = {
            "username": self.user.username,
            "password": "testing"
        }
        response = self.make_request("auth-login", kind="post", data=user_data)
        # assert token key exists
        self.assertIn("token", response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthRegisterUserTest(BaseViewTest):
    """
        Tests for auth/register/ endpoint
    """

    def test_register_user_with_invalid_data(self):
        """
            Test register user with invalid data
        """

        user_data = {
            "password": "",
            "email": ""
        }
        response = self.make_request("auth-register", kind="post", data=user_data)
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user(self):
        """
            Test register user with valid data
        """

        user_data = {
            "password": "new_pass",
            "email": "new_user@mail.com",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.make_request("auth-register", kind="post", data=user_data)
        # assert status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="new_user@mail.com")
        self.assertEqual(user.email, "new_user@mail.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")
