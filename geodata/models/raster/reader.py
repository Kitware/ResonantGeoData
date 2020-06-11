"""Helper methods for creating a ``GDALRaster`` entry from a raster file."""
from celery.utils.log import get_task_logger
from django.contrib.gis.gdal import GDALRaster, SpatialReference
from django.contrib.gis.geos import Polygon
import rasterio

# from django.core.files.base import ContentFile
# import io
# from PIL import Image

from .base import RasterEntry, RasterFile
from ..common import _ReaderRoutine

logger = get_task_logger(__name__)


class RasterEntryReader(_ReaderRoutine):
    """Raster injestion routine.

    This helper class will open a raster file and create the ``GDALRaster``
    for the ``RasterEntry``'s raster property.

    """

    # @staticmethod
    # def create_thumbnail(src):
    #     oview = int(max(src.height, src.width) * 0.1) or 1
    #     thumbnail = src.read(1, out_shape=(1, int(src.height // oview), int(src.width // oview)))
    #
    #     buf = io.BytesIO()
    #     thumbnail.save(buf, format='JPEG')
    #     byte_im = buf.getvalue()
    #     return ContentFile(byte_im)

    def _read_files(self):
        """Load raster data files and creaet a ``GDALRaster``.

        TODO: this function will need to handle a lot of scenarios for how
        the raster file is passed and where it is stored.

        """
        # Fetch the raster file this Layer corresponds to
        self.rfe = RasterFile.objects.get(id=self.model_id)
        file_path = self.rfe.raster_file.name

        logger.info(f'The raster file path: {file_path}')

        self.raster_entry = RasterEntry()
        self.raster_entry.raster_file = self.rfe

        with rasterio.open(file_path) as src:
            self.raster_entry.number_of_bands = src.count
            self.raster_entry.driver = src.driver
            # thumbnail = RasterEntryReader.create_thumbnail(src)
            # self.raster_entry.thumbnail.save('thumbnail.jpg', thumbnail, save=True)

            spatial_ref = SpatialReference(src.crs.to_wkt())
            raster_dict = {
                # 'name': '', # file path,
                'srid': spatial_ref.srid,
                'width': src.width,
                'height': src.height,
                'origin': [src.bounds.left, src.bounds.top],
                'scale': src.res,
            }
            self.raster_entry.raster = GDALRaster(raster_dict)

            coords = (
                (src.bounds.left, src.bounds.top),
                (src.bounds.right, src.bounds.top),
                (src.bounds.right, src.bounds.bottom),
                (src.bounds.left, src.bounds.bottom),
                (src.bounds.left, src.bounds.top),  # Close the loop
            )

            self.raster_entry.footprint = Polygon(coords, srid=spatial_ref.srid)

        return True

    def _save_entries(self):
        """Save entries."""
        # Now actually save the raster entry!
        self.raster_entry.save()
        return
