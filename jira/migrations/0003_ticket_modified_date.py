# Generated by Django 2.0.2 on 2020-12-31 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0002_auto_20201230_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
