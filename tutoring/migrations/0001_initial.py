# Generated by Django 3.1.7 on 2021-04-02 11:53

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('comment', models.TextField()),
                ('rating', models.PositiveSmallIntegerField()),
                ('edited', models.BooleanField(default=False)),
                ('dislikes', models.ManyToManyField(related_name='tutorReviewDislikes', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='tutorReviewLikes', to=settings.AUTH_USER_MODEL)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer', to=settings.AUTH_USER_MODEL)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'TutorReview',
            },
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=1024)),
                ('question', models.TextField()),
                ('answer', models.TextField(null=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('answerer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answerer', to=settings.AUTH_USER_MODEL)),
                ('dislikes', models.ManyToManyField(related_name='dislikes', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('questioner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questioner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'QuestionAnswer',
            },
        ),
        migrations.CreateModel(
            name='QAComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('edited', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('dislikes', models.ManyToManyField(related_name='qacomment_dislikes', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='qacomment_likes', to=settings.AUTH_USER_MODEL)),
                ('question_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutoring.questionanswer')),
            ],
            options={
                'verbose_name_plural': 'QAComments',
            },
        ),
    ]
