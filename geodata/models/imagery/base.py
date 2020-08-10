"""Base classes for raster dataset entries."""
import os

from django.contrib.gis.db import models
from django.contrib.postgres import fields
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from s3_file_field import S3FileField

from .ifiles import ImageFile
from ..common import ChecksumFile, ModifiableEntry, SpatialEntry
from ..mixins import TaskEventMixin
from ... import tasks


class ImageEntry(ModifiableEntry):
    """Single image entry, tracks the original file."""

    def __str__(self):
        return f'{self.name} ({self.id})'

    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    instrumentation = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='The instrumentation used to acquire these data.',
    )

    image_file = models.OneToOneField(ImageFile, null=True, on_delete=models.CASCADE)
    driver = models.CharField(max_length=100)

    # thumbnail = models.ImageField(blank=True, upload_to='thumbnails')

    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    number_of_bands = models.PositiveIntegerField()
    metadata = fields.JSONField(null=True)


class ImageSet(ModifiableEntry):
    """Container for many images."""

    def __str__(self):
        return f'{self.name} ({self.id} - {type(self)}'

    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    images = models.ManyToManyField(ImageEntry)

    @property
    def image_bands(self):
        return self.images.aggregate(models.Sum('number_of_bands'))['number_of_bands__sum']

    @property
    def width(self):
        return self.images.aggregate(models.Max('width'))['width__max']

    @property
    def height(self):
        return self.images.aggregate(models.Max('height'))['height__max']

    @property
    def count(self):
        return self.images.count()


@receiver(m2m_changed, sender=ImageSet.images.through)
def _m2m_changed_image_set(sender, instance, action, reverse, *args, **kwargs):
    # If no name was specified for an ImageSet, when images are added to it,
    # use the common base name of all images as the name of the ImageSet.
    if action == 'post_add' and not instance.name and instance.images.count():
        names = [image.name for image in instance.images.all() if image.name]
        if len(names):
            instance.name = os.path.commonprefix(names)
            instance.save(update_fields=['name'])


class RasterEntry(ImageSet, SpatialEntry, TaskEventMixin):
    """This class is a container for the metadata of a raster.

    This model inherits from ``ImageSet`` and only adds an extra layer of
    geospatial context to the ``ImageSet``.

    """

    def __str__(self):
        return 'ID: {} {} (type: {})'.format(self.id, self.name, type(self))

    # Raster fields
    crs = models.TextField(help_text='PROJ string', null=True)  # PROJ String
    origin = fields.ArrayField(models.FloatField(), size=2, null=True)
    extent = fields.ArrayField(models.FloatField(), size=4, null=True)
    resolution = fields.ArrayField(models.FloatField(), size=2, null=True)  # AKA scale
    # TODO: skew/transform
    transform = fields.ArrayField(models.FloatField(), size=6, null=True)

    task_func = tasks.task_populate_raster_entry
    failure_reason = models.TextField(null=True, blank=True)


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
    parent_image = models.ForeignKey(ImageEntry, on_delete=models.CASCADE)
    interpretation = models.TextField(null=True, blank=True)


class ConvertedImageFile(ChecksumFile):
    """A model to store converted versions of a raster entry."""

    file = S3FileField()
    failure_reason = models.TextField(null=True, blank=True)
    source_image = models.ForeignKey(ImageEntry, on_delete=models.CASCADE)


@receiver(post_save, sender=RasterEntry)
def _post_save_raster_entry(sender, instance, *args, **kwargs):
    transaction.on_commit(lambda: instance._on_commit_event_task(*args, **kwargs))
