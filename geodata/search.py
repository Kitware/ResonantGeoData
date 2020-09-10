import datetime
import json

import dateutil.parser
from django.contrib.gis.db.models import Collect, Extent
from django.contrib.gis.geos import Point
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Max, Min, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
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
        query.add(Q(footprint__distance_lte=(geom, float(params.get('radius', 0)))), Q.AND)
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
    operation_summary='List geospatial datasets near a point',
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
    operation_summary='List raster datasets near a point',
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
    operation_summary='List geometry datasets near a point',
    operation_description='List geospatial geometry datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point_geometry(request, *args, **kwargs):
    params = request.query_params
    results = GeometryEntry.objects.filter(search_near_point_filter(params))
    return JsonResponse(serializers.GeometryEntrySerializer(results, many=True).data, safe=False)


def extent_summary_spatial(found):
    """
    Given a query set of SpatialEntry, return a result dictionary with the summary.

    :param found: a query set with SpatialEntry results.
    :returns: a dictionary with count, collect, convex_hull, extent,
        acquisition, acqusition_date.  collect and convex_hull are geojson
        objects.
    """
    if found and found.count():
        summary = found.aggregate(
            Collect('footprint'),
            Extent('footprint'),
            Min('acquisition_date'),
            Max('acquisition_date'),
        )
        results = {
            'count': found.count(),
            'collect': json.loads(summary['footprint__collect'].geojson),
            'convex_hull': json.loads(summary['footprint__collect'].convex_hull.geojson),
            'extent': {
                'xmin': summary['footprint__extent'][0],
                'ymin': summary['footprint__extent'][1],
                'xmax': summary['footprint__extent'][2],
                'ymax': summary['footprint__extent'][3],
            },
            'acquisition_date': [
                summary['acquisition_date__min'].isoformat()
                if summary['acquisition_date__min'] is not None
                else None,
                summary['acquisition_date__max'].isoformat()
                if summary['acquisition_date__max'] is not None
                else None,
            ],
        }
    else:
        results = {'count': 0}
    return results


def extent_summary_modifiable(found):
    """
    Given a query set of ModifiableEntry, return a result dictionary with the summary.

    :param found: a query set with SpatialEntry results.
    :returns: a dictionary with count, collect, convex_hull, extent,
        acquisition, acqusition_date, created, modified.  collect and
        convex_hull are geojson objects.
    """
    if found and found.count():
        summary = found.aggregate(
            Min('created'),
            Max('created'),
            Min('modified'),
            Max('modified'),
        )
        results = {
            'count': found.count(),
            'created': [summary['created__min'].isoformat(), summary['created__max'].isoformat()],
            'modified': [
                summary['modified__min'].isoformat(),
                summary['modified__max'].isoformat(),
            ],
        }
    else:
        results = {'count': 0}
    return results


def extent_summary(found):
    results = extent_summary_modifiable(found)
    results.update(extent_summary_spatial(found))
    return results


def extent_summary_http(found):
    """
    Given a query set of items, return an http response with the summary.

    :param found: a query set with SpatialEntry results.
    :returns: an HttpResponse.
    """
    results = extent_summary(found)
    return HttpResponse(json.dumps(results), content_type='application/json')


@swagger_auto_schema(
    method='GET',
    operation_summary='Extents of geospatial datasets near a point',
    operation_description='Get the convex hull and time range for geospatial datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point_extent(request, *args, **kwargs):
    params = request.query_params
    found = SpatialEntry.objects.filter(search_near_point_filter(params))
    return extent_summary_http(found)


@swagger_auto_schema(
    method='GET',
    operation_summary='Extents of raster datasets near a point',
    operation_description='Get the convex hull and time range for geospatial raster datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point_extent_raster(request, *args, **kwargs):
    params = request.query_params
    found = RasterEntry.objects.filter(search_near_point_filter(params))
    return extent_summary_http(found)


@swagger_auto_schema(
    method='GET',
    operation_summary='Extents of geometry datasets near a point',
    operation_description='Get the convex hull and time range for geospatial geometry datasets near a specific latitude and longitude',
    query_serializer=NearPointSerializer,
)
@api_view(['GET'])
def search_near_point_extent_geometry(request, *args, **kwargs):
    params = request.query_params
    found = GeometryEntry.objects.filter(search_near_point_filter(params))
    return extent_summary_http(found)
