"""Helper methods for creating a geometry entries from uploaded files."""
from glob import glob
import os
import zipfile

from celery.utils.log import get_task_logger
from django.contrib.gis.geos import GeometryCollection, GEOSGeometry
from django.core.exceptions import ValidationError
import fiona
from shapely.geometry import shape
from shapely.wkb import dumps

from .base import GeometryArchive, GeometryEntry
from ..common import _ReaderRoutine
from ..constants import DB_SRID

logger = get_task_logger(__name__)


class GeometryArchiveReader(_ReaderRoutine):
    """Shapefile geometry injestion routine."""

    def _read_files(self):
        """Read an archive of a single shapefile (and associated) files.

        This will load zipped archives of shape files and create entries
        for a single shapefile (basename of files).

        A single shapefile will consist of a collection of one or many features
        of varying types. We produce a single ``GeometryCollection`` of those
        data. Hence, we associate a single shapefile with a single
        ``GeometryCollection``.

        We may need to do more checks/validation to make sure the user only
        added a single shape file or provide a more explicit upload interface
        where they upload the ``shp``, ``dbf``, etc. files individually and
        we assert that they match.

        """
        self.archive = GeometryArchive.objects.get(id=self.model_id)
        file_path = self.archive.archive_file.name
        logger.info(f'The geometry archive: {file_path}')

        # Unzip the contents to the working dir
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.tmpdir)
        shape_files = glob(os.path.join(self.tmpdir, '*.shp'))
        if len(shape_files) != 1:
            raise ValidationError('There must be one and only one shapefile in the archive.')
        shape_file = shape_files[0]

        # load each shapefile using fiona
        shapes = fiona.open(shape_file)

        # create a model entry for that shapefile
        if self.archive.geometry_entry is None:
            self.archive.geometry_entry = GeometryEntry()
            self.archive.geometry_entry.creator = self.archive.creator
        self.archive.geometry_entry.modifier = self.archive.modifier

        shapes.meta  # TODO: dump this JSON into the model entry

        collection = []
        for item in shapes:
            geom = shape(item['geometry'])  # not optimal?
            collection.append(GEOSGeometry(memoryview(dumps(geom, srid=DB_SRID))))
        self.archive.geometry_entry.data = GeometryCollection(*collection)

        return True

    def _save_entries(self):
        self.archive.geometry_entry.save()
        self.archive.save(update_fields=['geometry_entry'])
        return
