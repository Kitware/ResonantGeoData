# Generated by Django 3.0.6 on 2020-05-05 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_scorealgorithm_docker_image_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoreresult',
            name='overall_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]