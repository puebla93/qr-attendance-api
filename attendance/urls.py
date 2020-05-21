from django.urls import path

from .views import *

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('students/', ListStudentsView.as_view(), name="students-all"),
    path('teachers/', ListTeachersView.as_view(), name="teachers-all"),
    path('class_types/', ListClassTypesView.as_view(), name="class_types-all"),
    path('courses/', ListCoursesView.as_view(), name="courses-all"),
    path('attendances/', ListAttendancesView.as_view(), name="attendances-all")
]
