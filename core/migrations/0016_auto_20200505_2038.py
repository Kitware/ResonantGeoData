# Generated by Django 3.0.6 on 2020-05-05 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20200505_2032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoreresult',
            name='overall_score',
            field=models.FloatField(blank=True, default=0.9910551369828001, null=True),
        ),
    ]