# Generated by Django 3.0.6 on 2020-05-07 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20200505_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='algorithmjob',
            name='fail_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scorejob',
            name='fail_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
