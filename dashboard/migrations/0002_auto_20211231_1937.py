# Generated by Django 3.1.7 on 2021-12-31 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersession',
            name='ipAddress',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]