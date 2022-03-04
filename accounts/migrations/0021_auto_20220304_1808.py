# Generated by Django 3.1.7 on 2022-03-04 18:08

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20220304_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentprofile',
            name='dateOfBirth',
            field=models.DateField(blank=True, null=True, validators=[accounts.models.MinAgeValidator(18)]),
        ),
        migrations.AlterField(
            model_name='parentprofile',
            name='code',
            field=models.CharField(default=accounts.models.getParentCode, editable=False, max_length=8, unique=True),
        ),
    ]
