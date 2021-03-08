# Generated by Django 3.2a1 on 2021-03-08 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0004_auto_20210302_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checksumfile',
            name='name',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='fmventry',
            name='name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='geometryentry',
            name='name',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='imageentry',
            name='name',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='imageset',
            name='name',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='kwcocoarchive',
            name='name',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='rasterentry',
            name='name',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
