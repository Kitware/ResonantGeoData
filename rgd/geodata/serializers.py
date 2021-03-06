import json

from rest_framework import serializers
from rest_framework.reverse import reverse

from rgd import utility
from rgd.geodata.permissions import check_write_perm

from . import models


class SpatialEntrySerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        ret = super().to_representation(value)
        ret['footprint'] = json.loads(value.footprint.geojson)
        ret['outline'] = json.loads(value.outline.geojson)
        # Add hyperlink to get view for subtype if SpatialEntry
        if type(value).__name__ != value.subentry_type:
            subtype = value.subentry_type
            ret['subentry_type'] = subtype
            ret['subentry_pk'] = value.subentry.pk
            ret['subentry_name'] = value.subentry_name
            if subtype == 'RasterMetaEntry':
                ret['subentry_pk'] = value.subentry.pk
                subtype_uri = reverse('raster-meta-entry', args=[value.subentry.pk])
            elif subtype == 'GeometryEntry':
                subtype_uri = reverse('geometry-entry', args=[value.subentry.pk])
            elif subtype == 'FMVEntry':
                subtype_uri = reverse('fmv-entry', args=[value.subentry.pk])
            if 'request' in self.context:
                request = self.context['request']
                ret['detail'] = request.build_absolute_uri(subtype_uri)
            else:
                ret['detail'] = subtype_uri
        return ret

    class Meta:
        model = models.SpatialEntry
        fields = '__all__'


class GeometryEntrySerializer(SpatialEntrySerializer):
    class Meta:
        model = models.GeometryEntry
        exclude = ['data']


class GeometryEntryDataSerializer(GeometryEntrySerializer):
    def to_representation(self, value):
        ret = super().to_representation(value)
        ret['data'] = json.loads(value.data.geojson)
        return ret

    class Meta:
        model = models.GeometryEntry
        fields = '__all__'


class ConvertedImageFileSerializer(serializers.ModelSerializer):
    def validate_source_image(self, value):
        if 'request' in self.context:
            check_write_perm(self.context['request'].user, value)
        return value

    class Meta:
        model = models.ConvertedImageFile
        fields = '__all__'
        read_only_fields = ['id', 'status', 'failure_reason', 'converted_file']


class ChecksumFileSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        ret = super().to_representation(value)
        ret['download_url'] = value.get_url()
        return ret

    class Meta:
        model = models.ChecksumFile
        fields = '__all__'
        read_only_fields = ['id', 'checksum', 'last_validation', 'modified', 'created']


class SubsampledImageSerializer(serializers.ModelSerializer):

    data = ChecksumFileSerializer(read_only=True)

    def validate_source_image(self, value):
        if 'request' in self.context:
            check_write_perm(self.context['request'].user, value)
        return value

    def to_representation(self, value):
        ret = super().to_representation(value)
        realtive_status_uri = reverse('subsampled-status', args=[value.id])
        if 'request' in self.context:
            request = self.context['request']
            ret['status'] = request.build_absolute_uri(realtive_status_uri)
        else:
            ret['status'] = realtive_status_uri
        return ret

    class Meta:
        model = models.SubsampledImage
        fields = '__all__'
        read_only_fields = [
            'id',
            'status',
            'failure_reason',
            'data',
        ]

    def create(self, validated_data):
        """Prevent duplicated subsamples from being created."""
        obj, created = models.SubsampledImage.objects.get_or_create(**validated_data)
        if not created:
            # Trigger save event to reprocess the subsampling
            obj.save()
        return obj


class ImageFileSerializer(serializers.ModelSerializer):
    file = ChecksumFileSerializer()

    class Meta:
        model = models.ImageFile
        fields = '__all__'


class ImageEntrySerializer(serializers.ModelSerializer):
    image_file = ImageFileSerializer()

    def to_representation(self, value):
        ret = super().to_representation(value)
        realtive_thumbnail_uri = reverse('image-thumbnail', args=[value.id])
        if 'request' in self.context:
            request = self.context['request']
            ret['thumbnail'] = request.build_absolute_uri(realtive_thumbnail_uri)
        else:
            ret['thumbnail'] = realtive_thumbnail_uri
        return ret

    class Meta:
        model = models.ImageEntry
        fields = '__all__'
        read_only_fields = [
            'id',
            'modified',
            'created',
            'driver',
            'height',
            'width',
            'number_of_bands',
        ]


class ImageSetSerializer(serializers.ModelSerializer):
    images = ImageEntrySerializer(many=True)

    class Meta:
        model = models.ImageSet
        fields = '__all__'
        read_only_fields = [
            'id',
            'modified',
            'created',
        ]


class RasterEntrySerializer(serializers.ModelSerializer):
    image_set = ImageSetSerializer()
    ancillary_files = ChecksumFileSerializer(many=True)

    class Meta:
        model = models.RasterEntry
        fields = '__all__'


class RasterMetaEntrySerializer(SpatialEntrySerializer):
    parent_raster = RasterEntrySerializer()

    class Meta:
        model = models.RasterMetaEntry
        fields = '__all__'


class FMVFileSerializer(serializers.ModelSerializer):
    file = ChecksumFileSerializer()

    class Meta:
        model = models.FMVFile
        fields = '__all__'


class FMVEntrySerializer(SpatialEntrySerializer):
    fmv_file = FMVFileSerializer()

    class Meta:
        model = models.FMVEntry
        exclude = ['ground_frames', 'ground_union', 'flight_path', 'frame_numbers']


class FMVEntryDataSerializer(FMVEntrySerializer):
    def to_representation(self, value):
        ret = super().to_representation(value)
        ret['ground_frames'] = json.loads(value.ground_frames.geojson)
        ret['ground_union'] = json.loads(value.ground_union.geojson)
        ret['flight_path'] = json.loads(value.flight_path.geojson)
        return ret

    class Meta:
        model = models.FMVEntry
        fields = '__all__'


utility.make_serializers(globals(), models)
