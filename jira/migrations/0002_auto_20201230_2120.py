# Generated by Django 2.0.2 on 2020-12-30 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'verbose_name_plural': 'Ticket'},
        ),
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.CharField(default='None', max_length=16),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(default='None', max_length=16),
        ),
    ]
