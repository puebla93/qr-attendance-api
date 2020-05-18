import datetime
import random

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from .models import Attendances
from .serializers import AttendancesSerializer

# tests for views


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def valid_id(id):
        try:
            datetime.datetime(int("19"+id[:2]), int(id[2:4]), int(id[4:6]))
        except ValueError:
            try:
                datetime.datetime(int("20"+id[:2]), int(id[2:4]), int(id[4:6]))
            except ValueError:
                return False

        return True

    @staticmethod
    def get_random_ids(k):
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
    def create_attendance(
            student_id="", student_name="", teacher="", date="", course_name="", class_type="", details=""):
        if BaseViewTest.valid_id(student_id) and student_name != "" and teacher != "" and date != "" and course_name != "" and class_type != "" and details != "":
            Attendances.objects.create(student_id=student_id, student_name=student_name, teacher=teacher, date=date,
                                       course_name=course_name, class_type=class_type, details=details)

    def setUp(self):
        # add test data
        ids = BaseViewTest.get_random_ids(4)
        names = ["John Dow", "Jane Doe", "John Smith", "Jane Smith"]
        dates = [datetime.datetime.now() - datetime.timedelta(days=days) for days in range(4)]
        course_name = ["Programming", "Artificial Intelligence", "Computer Architecture", "Computer Vision"]
        class_type = ["Final Test", "Lab Lesson", "Practical Lesson", "Conference"]
        details = ["", "Lesson Before Final Test", "Last Practical Lesson", "First Conference"]
        [self.create_attendance(ids[i], names[i], names[i], dates[i], course_name[i],
                                class_type[i], details[i]) for i in range(4)]


class GetAllAttendancesTest(BaseViewTest):

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
