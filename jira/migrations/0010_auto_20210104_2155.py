# Generated by Django 2.0.2 on 2021-01-04 21:55

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jira', '0009_auto_20210103_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('edited', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jira.Ticket')),
                ('ticket_comment_dislikes', models.ManyToManyField(related_name='ticket_comment_dislikes', to=settings.AUTH_USER_MODEL)),
                ('ticket_comment_likes', models.ManyToManyField(related_name='ticket_comment_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'TicketComment',
            },
        ),
        migrations.AlterField(
            model_name='sprint',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2021, 1, 18, 21, 55, 23, 363101)),
        ),
    ]
