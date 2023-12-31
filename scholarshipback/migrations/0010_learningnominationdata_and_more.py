# Generated by Django 4.0.1 on 2022-01-20 12:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scholarshipback', '0009_datainfomiracle_point_request_data_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningNominationData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('linkgradebook', models.FileField(upload_to='uploads/')),
                ('excellent_mark_pecent', models.CharField(default='0', max_length=256, verbose_name='Очкнка(отлично),%')),
                ('student_exam_point', models.PositiveIntegerField(default=0, verbose_name='Оценка за экзамены (выставляет студент)')),
                ('admin_exam_point', models.PositiveIntegerField(default=0, verbose_name='Балл за оценку за экзамены (выставляет админ)')),
            ],
        ),
        migrations.RemoveField(
            model_name='datainfomiracle',
            name='excellent_mark_pecent',
        ),
        migrations.RemoveField(
            model_name='datainfomiracle',
            name='linkgradebook',
        ),
        migrations.RemoveField(
            model_name='request',
            name='admin_exam_point',
        ),
        migrations.RemoveField(
            model_name='request',
            name='student_exam_point',
        ),
        migrations.AlterField(
            model_name='datainfomiracle',
            name='point',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='request',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 20, 14, 27, 26, 378634), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='request',
            name='LastUpdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 20, 14, 27, 26, 378634), verbose_name='Последнее изменеиние'),
        ),
        migrations.AlterField(
            model_name='request',
            name='comments',
            field=models.ManyToManyField(blank=True, to='scholarshipback.Comments'),
        ),
        migrations.AddField(
            model_name='request',
            name='learning_nomination_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scholarshipback.learningnominationdata'),
        ),
    ]
