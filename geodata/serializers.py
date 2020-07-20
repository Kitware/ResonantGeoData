import json

from rest_framework import serializers

from rgd import utility
from . import models


class SpatialEntrySerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        ret = super().to_representation(value)
        ret['footprint'] = json.loads(value.footprint.geojson)
        return ret

    class Meta:
        model = models.SpatialEntry
        fields = '__all__'


class GeometryEntrySerializer(SpatialEntrySerializer):
    class Meta:
        model = models.GeometryEntry
        exclude = ['data']


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dataset
        ref_name = 'Geodata_Dataset'
        fields = '__all__'


utility.make_serializers(globals(), models)
