# Generated by Django 2.0.2 on 2021-01-23 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_message_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.TimeField(auto_now_add=True),
        ),
    ]