"""Base classes for raster dataset entries."""
from django.contrib.gis.db import models
from django.contrib.postgres import fields
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from s3_file_field import S3FileField

from ..common import ModifiableEntry, SpatialEntry
from ..mixins import PostSaveEventMixin
from ... import tasks


class RasterFile(ModifiableEntry, PostSaveEventMixin):
    """This is a standalone DB entry for raster files.

    This will automatically generate a ``RasterEntry`` on the ``post_save``
    event. This points to data in its original location and the generated
    ``RasterEntry`` points to this.

    TODO: support file collections (e.g. one Landsat 8 entry may need to point
    to a file for each band).

    """

    task_func = tasks.validate_raster
    name = models.CharField(max_length=100, blank=True, null=True)
    # TODO: does `raster_file` handle all our use cases?
    raster_file = S3FileField(upload_to='files/rasters')
    failure_reason = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.raster_file.name
        super(RasterFile, self).save(*args, **kwargs)


class RasterEntry(SpatialEntry):
    """This class is a container for the metadata of a raster.

    This model does not hold any raster data, only the metadata, and points
    to a ``RasterFile`` in which keeps track of the actual data.

    """

    instrumentation = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='The instrumentation used to acquire these data.',
    )

    # READ ONLY ATTRIBUTES
    # i.e. these are populated programatically by the ETL routine

    raster_file = models.OneToOneField(RasterFile, null=True, on_delete=models.CASCADE)
    # thumbnail = models.ImageField(blank=True, upload_to='thumbnails')

    # Raster fields
    crs = models.TextField(help_text='PROJ string')  # PROJ String
    origin = fields.ArrayField(models.FloatField(), size=2)
    extent = fields.ArrayField(models.FloatField(), size=4)
    resolution = fields.ArrayField(models.FloatField(), size=2)  # AKA scale
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    number_of_bands = models.PositiveIntegerField()
    driver = models.CharField(max_length=100)
    metadata = fields.JSONField(null=True)
    # TODO: skew/transform
    transform = fields.ArrayField(models.FloatField(), size=6)


class BandMetaEntry(ModifiableEntry):
    """A basic container to keep track of useful band info."""

    description = models.TextField(
        null=True,
        blank=True,
        help_text='Automatically retreived from raster but can be overwritten.',
    )
    dtype = models.CharField(max_length=10)
    max = models.FloatField(null=True)
    min = models.FloatField(null=True)
    mean = models.FloatField(null=True)
    std = models.FloatField(null=True)
    nodata_value = models.FloatField(null=True)
    parent_raster = models.ForeignKey(RasterEntry, on_delete=models.CASCADE)
    interpretation = models.TextField(null=True, blank=True)


class ConvertedRasterFile(ModifiableEntry):
    """A model to store converted versions of a raster entry."""

    converted_file = S3FileField()  # TODO: is this correct?
    failure_reason = models.TextField(null=True, blank=True)
    source_raster = models.ForeignKey(RasterEntry, on_delete=models.CASCADE)


@receiver(post_save, sender=RasterFile)
def _post_save_algorithm(sender, instance, *args, **kwargs):
    transaction.on_commit(lambda: instance._post_save(**kwargs))
