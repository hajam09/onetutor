# Generated by Django 2.0.2 on 2021-01-03 10:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0008_auto_20210102_0941'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sprint',
            options={'verbose_name_plural': 'Sprint'},
        ),
        migrations.AlterField(
            model_name='sprint',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2021, 1, 17, 10, 9, 21, 174680)),
        ),
    ]
