# Generated by Django 3.0.6 on 2020-05-22 18:45

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('student_id', models.CharField(max_length=11, unique=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='courses',
            name='course_details',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='attendances',
            name='details',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='classtypes',
            name='class_type',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='courses',
            name='course_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='attendances',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Users'),
        ),
        migrations.AlterField(
            model_name='attendances',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='teacher', to='attendance.Users'),
        ),
        migrations.DeleteModel(
            name='Students',
        ),
        migrations.DeleteModel(
            name='Teachers',
        ),
    ]