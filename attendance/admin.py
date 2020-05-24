from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

admin.site.register(ClassTypes)
admin.site.register(Courses)
admin.site.register(Users, UserAdmin)
admin.site.register(Attendances)
