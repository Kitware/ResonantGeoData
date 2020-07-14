# Generated by Django 3.0.7 on 2020-07-14 14:15

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0006_auto_20200713_1357'),
    ]

    operations = [
        migrations.RenameField(
            model_name='convertedrasterfile',
            old_name='converted_file',
            new_name='file',
        ),
        migrations.RenameField(
            model_name='geometryarchive',
            old_name='archive_file',
            new_name='file',
        ),
        migrations.RenameField(
            model_name='rasterfile',
            old_name='raster_file',
            new_name='file',
        ),
        migrations.AddField(
            model_name='convertedrasterfile',
            name='checksum',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='convertedrasterfile',
            name='compute_checksum',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='convertedrasterfile',
            name='last_validation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='convertedrasterfile',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='convertedrasterfile',
            name='validate_checksum',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='geometryarchive',
            name='checksum',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='geometryarchive',
            name='compute_checksum',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='geometryarchive',
            name='last_validation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='geometryarchive',
            name='validate_checksum',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rasterentry',
            name='data_mask',
            field=django.contrib.gis.db.models.fields.PolygonField(null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='rasterfile',
            name='checksum',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='rasterfile',
            name='compute_checksum',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rasterfile',
            name='last_validation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rasterfile',
            name='validate_checksum',
            field=models.BooleanField(default=False),
        ),
    ]
