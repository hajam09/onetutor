# Generated by Django 3.1.7 on 2021-04-02 11:53

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Countries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alpha', models.CharField(max_length=4)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name_plural': 'Countries',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name_plural': 'Subjects',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.CharField(max_length=256)),
                ('location', models.CharField(max_length=1024)),
                ('ip_address', models.GenericIPAddressField()),
                ('login_time', models.DateTimeField(default=datetime.datetime.now)),
                ('allowed', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'UserSessions',
            },
        ),
        migrations.CreateModel(
            name='TutorProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secondary_key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('summary', models.CharField(max_length=128)),
                ('about', models.TextField()),
                ('location', jsonfield.fields.JSONField(default=dict)),
                ('education', jsonfield.fields.JSONField(default=dict)),
                ('subjects', models.CharField(max_length=8192)),
                ('availability', jsonfield.fields.JSONField(default=dict)),
                ('profilePicture', models.ImageField(blank=True, default='profilepicture/defaultimg/default-profile-picture.jpg', null=True, upload_to='profilepicture')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'TutorProfiles',
            },
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', jsonfield.fields.JSONField(default=dict)),
                ('subjects', models.CharField(max_length=8192)),
                ('profilePicture', models.ImageField(blank=True, null=True, upload_to='profilepicture')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'StudentProfiles',
            },
        ),
        migrations.CreateModel(
            name='SocialConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter', models.CharField(blank=True, max_length=128)),
                ('facebook', models.CharField(blank=True, max_length=128)),
                ('google', models.CharField(blank=True, max_length=128)),
                ('linkedin', models.CharField(blank=True, max_length=128)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'SocialConnection',
            },
        ),
    ]