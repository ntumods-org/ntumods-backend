# Generated by Django 4.2.16 on 2024-09-12 07:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feedbackform',
            options={'verbose_name_plural': 'Feedback Forms'},
        ),
        migrations.RemoveField(
            model_name='feedbackform',
            name='response',
        ),
    ]