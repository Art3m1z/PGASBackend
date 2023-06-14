# Generated by Django 4.0.1 on 2022-01-22 09:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarshipback', '0015_alter_dictlevelprogress_createdon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dictlevelprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 22, 11, 0, 26, 891517)),
        ),
        migrations.AlterField(
            model_name='dictprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 22, 11, 0, 26, 891517)),
        ),
        migrations.AlterField(
            model_name='dictstatusprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 22, 11, 0, 26, 891517)),
        ),
        migrations.AlterField(
            model_name='dictviewprogress',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 22, 11, 0, 26, 891517)),
        ),
        migrations.AlterField(
            model_name='request',
            name='CreatedOn',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 22, 11, 0, 26, 891517), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='request',
            name='LastUpdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 22, 11, 0, 26, 891517), verbose_name='Последнее изменеиние'),
        ),
        migrations.RemoveField(
            model_name='request',
            name='data',
        ),
        migrations.AddField(
            model_name='request',
            name='data',
            field=models.ManyToManyField(to='scholarshipback.DataInfoMiracle'),
        ),
    ]