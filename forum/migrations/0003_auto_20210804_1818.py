# Generated by Django 3.1.7 on 2021-08-04 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0002_auto_20210721_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='dislikes',
            field=models.ManyToManyField(blank=True, related_name='communityDislikes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='community',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='communityLikes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='community',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='communityMembers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='forum',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forums', to='forum.community'),
        ),
        migrations.AlterField(
            model_name='forum',
            name='dislikes',
            field=models.ManyToManyField(blank=True, related_name='forumDislikes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='forum',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='forumLikes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='forum',
            name='watchers',
            field=models.ManyToManyField(blank=True, related_name='forumWatchers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='forumcomment',
            name='forum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forumComments', to='forum.forum'),
        ),
    ]
