# Generated by Django 5.1.1 on 2024-12-12 14:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_course_mutually_exclusive_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseschedule',
            name='common_schedule_for_course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='common_schedules', to='courses.course'),
        ),
    ]
