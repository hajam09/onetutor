# Generated by Django 3.1.7 on 2021-11-19 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20211030_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='profilePicture',
            field=models.ImageField(blank=True, default='avatars/parrot.png', null=True, upload_to='profile-picture'),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='profilePicture',
            field=models.ImageField(blank=True, default='avatars/dinosaur.png', null=True, upload_to='profile-picture'),
        ),
    ]