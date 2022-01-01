# Generated by Django 3.1.7 on 2021-11-21 19:08

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_tutorprofile_chargerate'),
        ('tutoring', '0006_feature_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='features',
            field=models.ManyToManyField(blank=True, related_name='tutorFeatures', to='tutoring.Feature'),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='profilePicture',
            field=models.ImageField(blank=True, default=accounts.models.getRandomImageForAvatar, null=True, upload_to='profile-picture'),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='profilePicture',
            field=models.ImageField(blank=True, default=accounts.models.getRandomImageForAvatar, null=True, upload_to='profile-picture'),
        ),
    ]