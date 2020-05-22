from django.urls import path

from .views import *

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', RegisterUsersView.as_view(), name="auth-register"),

    path('class_types/', ListClassTypesView.as_view(), name="class_types-all"),
    path('class_types/<str:type>/', ClassTypesDetailView.as_view(), name="class_types-detail"),

    path('courses/', ListCoursesView.as_view(), name="courses-all"),
    path('courses/<str:name>/', CoursesDetailView.as_view(), name="courses-detail"),

    path('attendances/', ListAttendancesView.as_view(), name="attendances-all"),
    path('attendances/', CreateAttendancesView.as_view(), name="attendances-create"),
    path('attendances/<int:id>/', AttendancesDetailView.as_view(), name="attendances-detail")
]
