from django.urls import path

from .views import *

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', RegisterUsersView.as_view(), name="auth-register"),

    path('class_types/', ListCreateClassTypesView.as_view(), name="class_types-list-create"),
    path('class_types/<str:type>/', ClassTypesDetailView.as_view(), name="class_types-detail"),

    path('courses/', ListCreateCoursesView.as_view(), name="courses-list-create"),
    path('courses/<str:name>/', CoursesDetailView.as_view(), name="courses-detail"),

    path('attendances/', ListCreateAttendancesView.as_view(), name="attendances-list-create"),
    path('attendances/<int:id>/', AttendancesDetailView.as_view(), name="attendances-detail")
]
