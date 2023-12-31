# Generated by Django 4.0.1 on 2022-01-24 19:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarshipback', '0016_alter_dictlevelprogress_createdon_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='learningPlan',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dictlevelprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 24, 21, 36, 56, 964951)),
        ),
        migrations.AlterField(
            model_name='dictprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 24, 21, 36, 56, 964951)),
        ),
        migrations.AlterField(
            model_name='dictstatusprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 24, 21, 36, 56, 964951)),
        ),
        migrations.AlterField(
            model_name='dictviewprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 24, 21, 36, 56, 964951)),
        ),
        migrations.AlterField(
            model_name='request',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 24, 21, 36, 56, 964951), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='request',
            name='LastUpdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 24, 21, 36, 56, 964951), verbose_name='Последнее изменеиние'),
        ),
        migrations.AlterField(
            model_name='request',
            name='learningPlan',
            field=models.CharField(max_length=255),
        ),
        migrations.DeleteModel(
            name='dictLearningPlan',
        ),
    ]
