import datetime

import dateutil.parser
from django.contrib.gis.geos import Point
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers as rfserializers
from rest_framework.decorators import api_view

from . import serializers
from .models import GeometryEntry, RasterEntry, SpatialEntry


class NearPointSerializer(rfserializers.Serializer):
    longitude = rfserializers.FloatField(required=False)
    latitude = rfserializers.FloatField(
        required=False, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    radius = rfserializers.FloatField(
        required=False, default=0, validators=[MinValueValidator(0)], help_text='Radius in meters'
    )
    # altitude = rfserializers.FloatField(
    #     allow_null=True, required=False, help_text='Altitude in meters'
    # )
    time = rfserializers.DateTimeField(allow_null=True, required=False)
    timespan = rfserializers.FloatField(
        required=False,
        default=86400,
        validators=[MinValueValidator(0)],
        help_text='Span in seconds on either size of the specified time',
    )
    timefield = rfserializers.CharField(
        required=False,
        default='acquisition',
        help_text='A comma-separated list of fields to search.  This can include acquisition, created, modified.',
    )


def search_near_point_filter(params):
    """
    Get a filter object that can be used when searching SpatialEntry models.

    :param params: a dictionary of parameters, optionally including
        latitude, longitude, radius, time, timespan, and timefield.
    :returns: a Django query (Q) object.
    """
    query = Q()
    if params.get('latitude') is not None and params.get('longitude') is not None:
        geom = Point(float(params['longitude']), float(params['latitude']))
        query.add(Q(footprint__distance_lte=(geom, float(params['radius']))), Q.AND)
    if params.get('time') is not None:
        qtime = dateutil.parser.isoparser().isoparse(params['time'])
        timespan = datetime.timedelta(0, float(params['timespan']))
        starttime = qtime - timespan
        endtime = qtime + timespan
        timefields = [field.strip() for field in params.get('timefield', '').split(',')] or [
            'acquisition'
        ]
        subquery = []
        for field in timefields:
            field_name = {
                'acquisition': 'acquisition_date',
                'created': 'created',
                'modified': 'modified',
            }.get(field)
            if not field_name:
                raise Exception('Unrecognized time field %s' % field)
            subquery.append(
                Q(**{'%s__gte' % field_name: starttime, '%s__lte' % field_name: endtime})
            )
            if field == 'acquisition':
                subquery.append(
                    Q(acquisition_date__isnull=True, created__gte=starttime, created__lte=endtime)
                )
        if subquery:
            for subq in subquery[1:]:
                subquery[0].add(subq, Q.OR)
            query.add(subquery[0], Q.AND)
    return query


@swagger_auto_schema(
    method='GET',
    operation_description='List geospatial datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point(request, *args, **kwargs):
    params = request.query_params
    results = SpatialEntry.objects.filter(search_near_point_filter(params))
    return JsonResponse(serializers.SpatialEntrySerializer(results, many=True).data, safe=False)


@swagger_auto_schema(
    method='GET',
    operation_description='List geospatial raster datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point_raster(request, *args, **kwargs):
    params = request.query_params
    results = RasterEntry.objects.filter(search_near_point_filter(params))
    return JsonResponse(serializers.RasterEntrySerializer(results, many=True).data, safe=False)


@swagger_auto_schema(
    method='GET',
    operation_description='List geospatial geometry datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point_geometry(request, *args, **kwargs):
    params = request.query_params
    results = GeometryEntry.objects.filter(search_near_point_filter(params))
    return JsonResponse(serializers.GeometryEntrySerializer(results, many=True).data, safe=False)
