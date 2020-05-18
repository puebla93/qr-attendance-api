# Generated by Django 3.0.6 on 2020-05-18 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendances',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=255)),
                ('student_name', models.CharField(max_length=255)),
                ('teacher', models.CharField(max_length=255)),
                ('date', models.DateField(editable=False)),
                ('course_name', models.CharField(max_length=255)),
                ('class_type', models.CharField(max_length=255)),
                ('details', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
