# Generated by Django 3.2a1 on 2021-03-10 20:00

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import s3_file_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('caption', models.CharField(blank=True, max_length=100, null=True)),
                ('label', models.CharField(blank=True, max_length=100, null=True)),
                ('annotator', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                (
                    'keypoints',
                    django.contrib.gis.db.models.fields.MultiPointField(null=True, srid=0),
                ),
                ('line', django.contrib.gis.db.models.fields.LineStringField(null=True, srid=0)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChecksumFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('checksum', models.CharField(max_length=128)),
                ('validate_checksum', models.BooleanField(default=False)),
                ('last_validation', models.BooleanField(default=True)),
                ('type', models.IntegerField(choices=[(1, 'FileField'), (2, 'URL')], default=1)),
                ('file', s3_file_field.fields.S3FileField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=127)),
            ],
            options={
                'default_related_name': 'collections',
            },
        ),
        migrations.CreateModel(
            name='ImageEntry',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                (
                    'instrumentation',
                    models.CharField(
                        blank=True,
                        help_text='The instrumentation used to acquire these data.',
                        max_length=100,
                        null=True,
                    ),
                ),
                ('driver', models.CharField(max_length=100)),
                ('height', models.PositiveIntegerField()),
                ('width', models.PositiveIntegerField()),
                ('number_of_bands', models.PositiveIntegerField()),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImageSet',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                ('images', models.ManyToManyField(to='geodata.ImageEntry')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Segmentation',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'outline',
                    django.contrib.gis.db.models.fields.PolygonField(
                        help_text='The bounding box', null=True, srid=0
                    ),
                ),
                (
                    'annotation',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.annotation'
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='SpatialEntry',
            fields=[
                ('spatial_id', models.AutoField(primary_key=True, serialize=False)),
                ('acquisition_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('footprint', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('outline', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='PolygonSegmentation',
            fields=[
                (
                    'segmentation_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='geodata.segmentation',
                    ),
                ),
                (
                    'feature',
                    django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=0),
                ),
            ],
            bases=('geodata.segmentation',),
        ),
        migrations.CreateModel(
            name='RLESegmentation',
            fields=[
                (
                    'segmentation_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='geodata.segmentation',
                    ),
                ),
                ('blob', models.BinaryField()),
                ('height', models.PositiveIntegerField()),
                ('width', models.PositiveIntegerField()),
            ],
            bases=('geodata.segmentation',),
        ),
        migrations.CreateModel(
            name='SubsampledImage',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                (
                    'sample_type',
                    models.CharField(
                        choices=[
                            ('pixel box', 'Pixel bounding box'),
                            ('geographic box', 'Geographic bounding box'),
                            ('geojson', 'GeoJSON feature'),
                            ('annotation', 'Annotation entry'),
                        ],
                        default='pixel box',
                        max_length=20,
                    ),
                ),
                ('sample_parameters', models.JSONField()),
                (
                    'data',
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='geodata.checksumfile',
                    ),
                ),
                (
                    'source_image',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.imageentry'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RasterEntry',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                (
                    'image_set',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.imageset'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KWCOCOArchive',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                (
                    'image_archive',
                    models.OneToOneField(
                        help_text='An archive (.tar or .zip) of the images referenced by the spec file (optional).',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='kwcoco_image_archive',
                        to='geodata.checksumfile',
                    ),
                ),
                (
                    'image_set',
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='geodata.imageset',
                    ),
                ),
                (
                    'spec_file',
                    models.OneToOneField(
                        help_text='The JSON spec file.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='kwcoco_spec_file',
                        to='geodata.checksumfile',
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                (
                    'file',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.checksumfile'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='imageentry',
            name='image_file',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to='geodata.imagefile'
            ),
        ),
        migrations.CreateModel(
            name='GeometryArchive',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                (
                    'file',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.checksumfile'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FMVFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                ('klv_file', s3_file_field.fields.S3FileField(null=True)),
                ('web_video_file', s3_file_field.fields.S3FileField(null=True)),
                ('frame_rate', models.FloatField(null=True)),
                (
                    'file',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.checksumfile'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConvertedImageFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                (
                    'converted_file',
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='geodata.checksumfile',
                    ),
                ),
                (
                    'source_image',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.imageentry'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionMembership',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'role',
                    models.SmallIntegerField(
                        choices=[(1, 'Reader'), (2, 'Owner')],
                        default=1,
                        help_text='A "reader" can view assets in this collection. An "owner" can additionally add/remove other users, set their permissions, delete the collection, and add/remove other files.',
                    ),
                ),
                (
                    'collection',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='collection_memberships',
                        to='geodata.collection',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='collection_memberships',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'default_related_name': 'collection_memberships',
            },
        ),
        migrations.AddField(
            model_name='collection',
            name='users',
            field=models.ManyToManyField(
                related_name='collections',
                through='geodata.CollectionMembership',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='checksumfile',
            name='collection',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='checksumfiles',
                related_query_name='checksumfiles',
                to='geodata.collection',
            ),
        ),
        migrations.CreateModel(
            name='BandMetaEntry',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('band_number', models.IntegerField()),
                (
                    'description',
                    models.TextField(
                        blank=True,
                        help_text='Automatically retreived from raster but can be overwritten.',
                        null=True,
                    ),
                ),
                ('dtype', models.CharField(max_length=10)),
                ('max', models.FloatField(null=True)),
                ('min', models.FloatField(null=True)),
                ('mean', models.FloatField(null=True)),
                ('std', models.FloatField(null=True)),
                ('nodata_value', models.FloatField(null=True)),
                ('interpretation', models.TextField()),
                (
                    'parent_image',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.imageentry'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='annotation',
            name='image',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='geodata.imageentry'
            ),
        ),
        migrations.CreateModel(
            name='RasterMetaEntry',
            fields=[
                (
                    'spatialentry_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='geodata.spatialentry',
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('crs', models.TextField(help_text='PROJ string')),
                (
                    'origin',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=2
                    ),
                ),
                (
                    'extent',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=4
                    ),
                ),
                (
                    'resolution',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=2
                    ),
                ),
                (
                    'transform',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), size=6
                    ),
                ),
                (
                    'parent_raster',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.rasterentry'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('geodata.spatialentry', models.Model),
        ),
        migrations.CreateModel(
            name='GeometryEntry',
            fields=[
                (
                    'spatialentry_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='geodata.spatialentry',
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                ('data', django.contrib.gis.db.models.fields.GeometryCollectionField(srid=4326)),
                (
                    'geometry_archive',
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='geodata.geometryarchive',
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('geodata.spatialentry', models.Model),
        ),
        migrations.CreateModel(
            name='FMVEntry',
            fields=[
                (
                    'spatialentry_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='geodata.spatialentry',
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('name', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                ('ground_frames', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('ground_union', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('flight_path', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
                ('frame_numbers', models.BinaryField()),
                (
                    'fmv_file',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='geodata.fmvfile'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('geodata.spatialentry', models.Model),
        ),
        migrations.AddConstraint(
            model_name='collectionmembership',
            constraint=models.UniqueConstraint(fields=('collection', 'user'), name='unique_user'),
        ),
        migrations.AddConstraint(
            model_name='checksumfile',
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ('file__regex', '.+'),
                        ('type', 1),
                        models.Q(('url__in', ['', None]), ('url__isnull', True), _connector='OR'),
                    ),
                    models.Q(
                        ('type', 2),
                        models.Q(('url__isnull', False), ('url__regex', '.+')),
                        models.Q(('file__in', ['', None]), ('file__isnull', True), _connector='OR'),
                    ),
                    _connector='OR',
                ),
                name='geodata_checksumfile_file_source_value_matches_type',
            ),
        ),
    ]
