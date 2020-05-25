# Generated by Django 3.0.6 on 2020-05-24 19:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0003_auto_20200524_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendances',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_attendances', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='attendances',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='teacher_attendances', to=settings.AUTH_USER_MODEL),
        ),
    ]