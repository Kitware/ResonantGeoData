# Generated by Django 3.0.6 on 2020-05-06 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20200506_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoreresult',
            name='overall_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]