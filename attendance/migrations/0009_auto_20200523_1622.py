# Generated by Django 3.0.6 on 2020-05-23 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_auto_20200523_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendances',
            name='date',
            field=models.DateField(editable=False),
        ),
    ]
