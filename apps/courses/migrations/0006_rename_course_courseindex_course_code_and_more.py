# Generated by Django 5.1.1 on 2024-12-09 16:49

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_alter_course_mutually_exclusive_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseindex',
            old_name='course',
            new_name='course_code',
        ),
        migrations.RemoveField(
            model_name='course',
            name='id',
        ),
        migrations.RemoveField(
            model_name='courseindex',
            name='id',
        ),
        migrations.RemoveField(
            model_name='courseindex',
            name='information',
        ),
        migrations.RemoveField(
            model_name='courseindex',
            name='schedule',
        ),
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(max_length=6, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='courseindex',
            name='index',
            field=models.CharField(max_length=5, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_format', message='The value must be 5 numeric digits.', regex='^\\d{5}$')]),
        ),
        migrations.CreateModel(
            name='CourseSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=200)),
                ('group', models.CharField(max_length=200)),
                ('day', models.CharField(max_length=200)),
                ('time', models.CharField(max_length=200)),
                ('venue', models.CharField(max_length=200)),
                ('remark', models.CharField(max_length=200)),
                ('schedule', models.CharField(max_length=200)),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='courses.courseindex')),
            ],
        ),
    ]