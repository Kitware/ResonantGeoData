import base64
import pickle

from django.contrib.gis.db import models
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from s3_file_field import S3FileField

from ... import tasks
from ..common import ChecksumFile, ModifiableEntry, SpatialEntry
from ..constants import DB_SRID
from ..mixins import TaskEventMixin


class FMVFile(ChecksumFile, TaskEventMixin):
    """For uploading single FMV files (mp4)."""

    task_func = tasks.task_read_fmv_file
    failure_reason = models.TextField(null=True, blank=True)
    file = S3FileField(upload_to='files/fmv/')


@receiver(post_save, sender=FMVFile)
def _post_save_fmv_file(sender, instance, *args, **kwargs):
    transaction.on_commit(lambda: instance._post_save_event_task(*args, **kwargs))


class FMVEntry(ModifiableEntry, SpatialEntry):
    """Single FMV entry, tracks the original file."""

    def __str__(self):
        return f'{self.name} ({self.id})'

    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    fmv_file = models.OneToOneField(FMVFile, null=True, on_delete=models.CASCADE)
    klv_file = S3FileField(upload_to='files/fmv/', null=True, blank=True)
    web_video_file = S3FileField(upload_to='files/fmv/web/', null=True, blank=True)
    frame_rate = models.FloatField(null=True, blank=True)

    ground_frames = models.MultiPolygonField(srid=DB_SRID, null=True, blank=True)
    ground_union = models.MultiPolygonField(srid=DB_SRID, null=True, blank=True)
    flight_path = models.MultiPointField(srid=DB_SRID, null=True, blank=True)
    frame_numbers = models.BinaryField(null=True, blank=True)

    @staticmethod
    def _array_to_blob(array):
        return base64.b64encode(pickle.dumps(array))

    @staticmethod
    def _blob_to_array(blob):
        return pickle.loads(base64.b64decode(blob))