import json
import os

from django.db.models.fields.files import FieldFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404  # , render
from django.utils.encoding import smart_str
from django.views import generic
from django.views.generic import DetailView
from rest_framework.decorators import api_view

from . import models
from . import search
from .models.imagery.base import RasterEntry


class RasterEntriesListView(generic.ListView):
    model = RasterEntry
    context_object_name = 'rasters'
    template_name = 'geodata/raster_entries.html'

    def get_queryset(self):
        # latitude, longitude, radius, time, timespan, and timefield
        search_params = {}
        for key in {'longitude', 'latitude', 'radius'}:
            if self.request.GET.get(key):
                try:
                    search_params[key] = float(self.request.GET.get(key))
                except ValueError:
                    pass
        return self.model.objects.filter(search.search_near_point_filter(search_params))

    def get_context_data(self, *args, **kwargs):
        # The returned query set is in self.object_list, not self.queryset
        context = super().get_context_data(*args, **kwargs)
        context['extents'] = json.dumps(search.extant_summary(self.object_list))
        return context


class RasterEntryDetailView(DetailView):
    model = RasterEntry


@api_view(['GET'])
def download_file(request, model, id, field):
    model_class = ''.join([part[:1].upper() + part[1:] for part in model.split('_')])
    if not hasattr(models, model_class):
        raise Exception('No such model (%s)' % model)
    model_inst = get_object_or_404(getattr(models, model_class), pk=id)
    if not isinstance(getattr(model_inst, field, None), FieldFile):
        raise Exception('No such file (%s)' % field)
    file = getattr(model_inst, field)
    filename = os.path.basename(file.name)
    if not filename:
        filename = '%s_%s_%s.dat' % (model, id, field)
    mimetype = getattr(
        model_inst,
        '%s_mimetype' % field,
        'text/plain' if field == 'log' else 'application/octet-stream',
    )
    response = HttpResponse(file.chunks(), content_type=mimetype)
    response['Content-Disposition'] = smart_str(u'attachment; filename=%s' % filename)
    if len(file) is not None:
        response['Content-Length'] = len(file)
    return response
