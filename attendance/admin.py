from django.contrib import admin

from .models import *

admin.site.register(Students)
admin.site.register(Teachers)
admin.site.register(ClassTypes)
admin.site.register(Courses)
admin.site.register(Attendances)
