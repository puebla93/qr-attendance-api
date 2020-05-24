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

    def setUp(self):
        # create a teacher user
        self.teacher = BaseViewTest.create_teacher(
            teacher_email="jonny@matcom.uh.cu",
            first_name="John",
            last_name="Doe",
        )
        # create a student user
        self.student = BaseViewTest.create_student(
            student_id=BaseViewTest.get_random_student_ids(1)[0],
            first_name="Jane",
            last_name="Doe",
        )

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
            remaining = [str(random.randrange(10)) for _ in range(5)]
            remaining = "".join(remaining)
            ids.append(year + month + day + remaining)

        return ids

    @staticmethod
    def create_student(student_id="", first_name="", last_name=""):
        if Users.is_valid_student_id(student_id) and first_name != "" and last_name != "":
            return Users.objects.create_user(
                username=student_id,
                password=student_id,
                first_name=first_name,
                last_name=last_name
            )

    @staticmethod
    def create_teacher(teacher_email="", first_name="", last_name=""):
        if Users.is_valid_teacher_email(teacher_email) and first_name != "" and last_name != "":
            return Users.objects.create_user(
                username=teacher_email,
                email=teacher_email,
                password="testing",
                first_name=first_name,
                last_name=last_name
            )

    @staticmethod
    def create_class_type(class_type=""):
        if class_type != "":
            return ClassTypes.objects.create(class_type=class_type)

    @staticmethod
    def create_course(course_name="", course_details="", teachers=[]):
        if course_name != "":
            course = Courses.objects.create(course_name=course_name, course_details=course_details)
            course.teachers.set(teachers)
            return course

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
        response = self.make_request("class_types-list-create")
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

        self.login_client(username=self.student.username, password=self.student.username)

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

        self.login_client(self.teacher.username, 'testing')

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

    def test_update_a_class_type_with_invalid_data(self):
        """
            This test ensures that a single class_type can't be updated without
            corresponding data
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint valid user
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        new_class_type = "New class type"
        response = self.make_request("class_types-detail", kind="put",
            data={"bad_class_type_key": new_class_type},
            type=class_type
        )
        self.assertEqual(
            response.data["message"],
            "class_type is required to create/update a class type"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_a_class_type(self):
        """
            This test ensures that a single class_type can be updated
        """

        self.login_client(self.teacher.username, 'testing')

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

        self.login_client(username=self.student.username, password=self.student.username)

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

        self.login_client(self.teacher.username, 'testing')

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

        self.login_client(self.teacher.username, 'testing')
        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.make_request("class_types-detail", kind="delete",
            type=class_type
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_a_class_type_no_logged_user(self):
        """
            This test ensures that to create a class type the user need to be logged
        """

        class_type = {"class_type": "Partial Exam"}

        # hit the API endpoint
        response = self.make_request("class_types-list-create", kind="post", data=class_type)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_a_class_type_no_authorized_user(self):
        """
            This test ensures that a unauthorized user can't create a class type
        """

        self.login_client(username=self.student.username, password=self.student.username)

        class_type = {"class_type": "Partial Exam"}

        # hit the API endpoint
        response = self.make_request("class_types-list-create", kind="post", data=class_type)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_a_class_type_with_invalid_data(self):
        """
            This test ensures that a single class type can't be created with invalid data
        """

        self.login_client(self.teacher.username, 'testing')

        invalid_class_type = {"bad_class_type_key": "New class type"}

        # test with invalid data
        response = self.make_request("class_types-list-create", kind="post", data=invalid_class_type)
        self.assertEqual(
            response.data["message"],
            "class_type is required to create/update a class type"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_class_type_that_already_exists(self):
        """
            This test ensures that a single class type can't be created
            if already exists
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        class_type = random.choice(ClassTypesViewTest.CLASS_TYPES)
        response = self.make_request("class_types-list-create", kind="post",
            data={"class_type": class_type})

        self.assertEqual(
            response.data["message"],
            "class type: {} already exists".format(class_type)
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_a_class_type(self):
        """
            This test ensures that a single class type can be created
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        class_type = {"class_type": "Partial Exam"}
        response = self.make_request("class_types-list-create", kind="post", data=class_type)

        self.assertEqual(response.data, class_type)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CoursesViewTest(BaseViewTest):
    """
        Tests for the courses/ endpoints
    """

    COURSE_NAMES = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]

    def setUp(self):
        super(CoursesViewTest, self).setUp()

        # add test data
        courses = [self.create_course(CoursesViewTest.COURSE_NAMES[i]) for i in range(4)]

        self.student_assistant = BaseViewTest.create_student(
            student_id=BaseViewTest.get_random_student_ids(1)[0],
            first_name="George",
            last_name="Smith",
        )
        self.student_assistant.teaching.set(courses)
        self.student_assistant.save()

    def test_get_all_courses(self):
        """
            This test ensures that all courses added in the setUp method
            exist when we make a GET request to the courses/ endpoint
        """

        # hit the API endpoint
        response = self.make_request("courses-list-create")
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
        course_data = {
            "course_name": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }
        response = self.make_request("courses-detail", kind="put",
            data=course_data, name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_a_course_no_course_teacher(self):
        """
            This test ensures that to update a course the user need to be
            a teacher of the course
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint unauthorized user
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        course_data = {
            "course_name": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }
        response = self.make_request("courses-detail", kind="put",
            data=course_data, name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_a_course_student_assistant(self):
        """
            This test ensures that a course student assistant user can't 
            update a course
        """

        self.login_client(
            username=self.student_assistant.username,
            password=self.student_assistant.username
        )

        # hit the API endpoint unauthorized user
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        course_data = {
            "course_name": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }
        response = self.make_request("courses-detail", kind="put",
            data=course_data, name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_a_course_that_does_not_exist(self):
        """
            This test try to update a course that doesn't exists and make assertions
        """

        self.login_client(self.teacher.username, 'testing')

        # test with invalid data
        course_name = "Operating System"
        course_data = {
            "course_name": "Compilation",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }
        response = self.make_request("courses-detail", kind="put",
            data=course_data,
            name=course_name
        )
        self.assertEqual(
            response.data["message"],
            "Course with name: \"{}\" does not exist".format(course_name)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_a_course_with_invalid_data(self):
        """
            This test ensures that a single course can't be updated without
            corresponding data
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint valid user
        course = random.choice(CoursesViewTest.COURSE_NAMES)
        course_data = {
            "bad_course_name_key": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }
        response = self.make_request("courses-detail", kind="put",
            data=course_data,
            name=course
        )
        self.assertEqual(response.data["message"], "course_name is required to create/update a course")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_a_course(self):
        """
            This test ensures that a single course can be updated
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint valid user
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        course_data = {
            'course_name': "Operating System",
            'course_details': "New course detail",
            "teachers": [self.teacher.username, self.student.username]
        }
        self.teacher.teaching.add(Courses.objects.filter(course_name=course_name).get())
        self.teacher.save()

        response = self.make_request("courses-detail", kind="put",
            data=course_data,
            name=course_name
        )
        self.assertEqual(response.data, course_data)
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
            This test ensures that to delete a course the user need to be
            a teacher of the course
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        response = self.make_request("courses-detail", kind="delete",
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_a_course_student_assistant(self):
        """
            This test ensures that a course student assistant user can't 
            delete a course
        """

        self.login_client(
            username=self.student_assistant.username,
            password=self.student_assistant.username
        )

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

        self.login_client(self.teacher.username, 'testing')

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

        self.login_client(self.teacher.username, 'testing')
        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        self.teacher.teaching.add(Courses.objects.filter(course_name=course_name).get())
        self.teacher.save()
        response = self.make_request("courses-detail", kind="delete",
            name=course_name
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_a_course_no_logged_user(self):
        """
            This test ensures that to create a course the user need to be logged
        """

        course = {
            "course_name": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }

        # hit the API endpoint
        response = self.make_request("courses-list-create", kind="post", data=course)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_a_course_no_authorized_user(self):
        """
            This test ensures that a unauthorized user can't create a course
        """

        self.login_client(
            username=self.student_assistant.username,
            password=self.student_assistant.username
        )

        course = {
            "course_name": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }

        # hit the API endpoint
        response = self.make_request("courses-list-create", kind="post", data=course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_a_course_with_invalid_data(self):
        """
            This test ensures that a single course can't be created with invalid data
        """

        self.login_client(self.teacher.username, 'testing')

        invalid_course = {
            "bad_course_name_key": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }

        # test with invalid data
        response = self.make_request("courses-list-create", kind="post", data=invalid_course)
        self.assertEqual(
            response.data["message"],
            "course_name is required to create/update a course"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_course_that_already_exists(self):
        """
            This test ensures that a single course can't be created
            if already exists
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        course_name = random.choice(CoursesViewTest.COURSE_NAMES)
        course = {"course_name": course_name}
        response = self.make_request("courses-list-create", kind="post", data=course)

        self.assertEqual(
            response.data["message"],
            "course: {} already exists".format(course_name)
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_a_course(self):
        """
            This test ensures that a single course can be created
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        course = {
            "course_name": "Operating System",
            "course_details": "New course details",
            "teachers": [self.teacher.username, self.student.username]
        }
        response = self.make_request("courses-list-create", kind="post", data=course)

        self.assertEqual(response.data, course)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AttendancesViewTest(BaseViewTest):
    """
        Tests for the attendances/ endpoint
    """

    def setUp(self):
        super(AttendancesViewTest, self).setUp()

        # adding test data
        self.student_assistant = BaseViewTest.create_student(
            student_id=BaseViewTest.get_random_student_ids(1)[0],
            first_name="George",
            last_name="Smith",
        )

        course_names = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]
        courses = [self.create_course(course_name) for course_name in course_names]
        self.student_assistant.teaching.add(courses[0])
        self.student_assistant.save()

        class_types = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]
        class_types = [self.create_class_type(class_type) for class_type in class_types]

        dates = [datetime.date.today() - datetime.timedelta(days=days) for days in range(4)]
        details = ["", "Lesson Before Final Test", "Last Practical Lesson", "First Conference"]
        students = [self.student, self.student_assistant]
        [self.create_attendance(students[i%2], self.teacher, dates[i], courses[i],
                                class_types[i], details[i]) for i in range(4)]

    def create_attendance_data(self, create_objects=True):
        student_id = BaseViewTest.get_random_student_ids(1)[0]
        student_name = ["Matcom", "Student"]
        course_name = "Operating System"
        class_type = "Partial Exam"
        details = "Class Details"
        date = datetime.date.today()
        iso_date = datetime.date.isoformat(date)

        if create_objects:
            self.create_student(student_id, student_name[0], student_name[1])
            self.create_course(course_name)
            self.create_class_type(class_type)

        return {
            "student_id": student_id,
            "student_name": student_name,
            "course_name": course_name,
            "class_type": class_type,
            "date": iso_date,
            "details": details
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

        self.login_client(username=self.student.username, password=self.student.username)

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

        self.login_client(username=self.student.username, password=self.student.username)

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

        self.login_client(username=self.student.username, password=self.student.username)

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

        self.login_client(username=self.student.username, password=self.student.username)

        attendance = self.create_attendance_data()

        # hit the API endpoint
        response = self.make_request("attendances-list-create", kind="post", data=attendance)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_an_attendance_with_invalid_data(self):
        """
            This test ensures that a single attendance can't be added with invalid data
        """

        self.login_client(self.teacher.username, 'testing')

        invalid_attendance = {}

        # test with invalid data
        response = self.make_request("attendances-list-create", kind="post", data=invalid_attendance)
        self.assertEqual(
            response.data["message"],
            "student_id, student_name, course_name, class_type and date are required to add an attendance"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_an_attendance_without_created_attendance_data(self):
        """
            This test ensures that a single attendance can be added without
            student, class type, course having been created before
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        attendance = self.create_attendance_data(create_objects=False)
        response = self.make_request("attendances-list-create", kind="post", data=attendance)

        attendance.update({'teacher_name':self.teacher.get_full_name()})
        attendance['student_name'] = " ".join(attendance['student_name'])
        self.assertEqual(response.data, attendance)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_an_attendance_by_a_student_assistant_bad_course(self):
        """
            This test ensures that a single attendance can't be added by a
            student assistant of other course
        """

        self.login_client(
            username=self.student_assistant.username, 
            password=self.student_assistant.username
        )

        # hit the API endpoint
        attendance = self.create_attendance_data()
        response = self.make_request("attendances-list-create", kind="post", data=attendance)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_an_attendance_by_a_student_assistant(self):
        """
            This test ensures that a single attendance can be added by one of its
            student assistants
        """

        self.login_client(
            username=self.student_assistant.username, 
            password=self.student_assistant.username
        )

        # hit the API endpoint
        attendance = self.create_attendance_data()
        student_assistant_course = self.student_assistant.teaching.all()[0]
        attendance['course_name'] = student_assistant_course.course_name
        response = self.make_request("attendances-list-create", kind="post", data=attendance)

        attendance.update({'teacher_name':self.student_assistant.get_full_name()})
        attendance['student_name'] = " ".join(attendance['student_name'])
        self.assertEqual(response.data, attendance)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_an_attendance(self):
        """
            This test ensures that a single attendance can be added
        """

        self.login_client(self.teacher.username, 'testing')

        # hit the API endpoint
        attendance = self.create_attendance_data()
        response = self.make_request("attendances-list-create", kind="post", data=attendance)

        attendance.update({'teacher_name':self.teacher.get_full_name()})
        attendance['student_name'] = " ".join(attendance['student_name'])
        self.assertEqual(response.data, attendance)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


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
            "username": self.student.username,
            "password": self.student.username
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

    def test_register_user_with_invalid_email(self):
        """
            Test register user with invalid email
        """

        user_data = {
            "username": "new_user@mail.com",
            "password": "pass"
        }
        response = self.make_request("auth-register", kind="post", data=user_data)
        self.assertEqual(response.data["message"], "email and password is required to register a user")
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_invalid_password(self):
        """
            Test register user with invalid password
        """
        user_data = {
            "username": "new_user@matcom.uh.cu",
            "password": ""
        }
        response = self.make_request("auth-register", kind="post", data=user_data)
        self.assertEqual(response.data["message"], "email and password is required to register a user")
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user(self):
        """
            Test register user with valid data
        """

        email = "new_user@matcom.uh.cu"
        user_data = {
            "username": email,
            "password": "new_pass",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.make_request("auth-register", kind="post", data=user_data)
        # assert status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['teaching'], [])
        self.assertEqual(response.data['username'], email)
        full_name = " ".join([user_data['first_name'], user_data['last_name']])
        self.assertEqual(response.data['full_name'], full_name)
        user = Users.objects.get(username=email)
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")
