# Generated by Django 4.0.5 on 2022-07-04 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarshipback', '0023_alter_datainfomiracle_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='compaing',
            name='show_student_points',
            field=models.BooleanField(default=True),
        ),
    ]
