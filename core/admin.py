import os

from django.contrib import admin
from django.db.models import FileField
from django.forms import TextInput
from django.template.defaultfilters import linebreaksbr
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django_admin_display import admin_display


from . import models
from . import tasks


def _text_preview(log_file: FileField):
    """
    Return the text of a file if it is short or the last portion of it if it is long.

    :params: log_file A FileField to read text from.
    """
    # max file size for display, currently 10kb
    maxlen = 10000
    if log_file:
        with log_file.open('rb') as datafile:
            if len(datafile) > 0:
                try:
                    datafile.seek(-maxlen, os.SEEK_END)
                except OSError as exc:
                    if exc.errno != 22:
                        # reraise exceptions except for trying to seek before the beginning
                        raise
                message = datafile.read().decode(errors='replace')
                if len(log_file) < maxlen:
                    return mark_safe('<PRE>' + escape(message) + '</PRE>')
                else:
                    prefix_message = f"""The output is too large to display in the browser.
                Only the last {maxlen} characters are displayed.
                """
                    prefix_message = linebreaksbr(prefix_message)
                    return mark_safe(prefix_message + '<PRE>' + escape(message) + '</PRE>')
            else:
                return 'Log is empty'
    else:
        return 'No log file to display'


def _result_preview(result: FileField, mimetype):
    mimetype_check = False
    # check number of / to determine how to parse the mimetype
    mimetype_number = mimetype.count('/')
    if mimetype_number == 1:
        # check if 'text' is the file type
        mimetype = mimetype.split('/')
        mimetype_first_part = mimetype[0]
        if mimetype_first_part == 'text':
            mimetype_check = True
    else:
        # if there are 2 mimetypes
        mimetype = mimetype.split('/')
        mimetype_first_part = mimetype[0]
        mimetype_second_part = mimetype[2]
        if mimetype_first_part == 'text' or mimetype_second_part == 'text':
            mimetype_check = True
    # show 10kb
    maxlen = 10000
    if mimetype_check:
        with result.open('rb') as datafile:
            if len(datafile) > 0:
                try:
                    # from the beginning to the maxlen
                    datafile.seek(maxlen, os.SEEK_SET)
                except OSError as exc:
                    if exc.errno != 22:
                        # reraise exceptions except for trying to seek before the beginning
                        raise
                message = datafile.read().decode(errors='replace')
                if len(result) < maxlen:
                    return mark_safe('<PRE>' + escape(message) + '</PRE>')
                else:
                    prefix_message = f"""The output is too large to display in the browser.
                Only the first {maxlen} characters are displayed.
                """
                    prefix_message = linebreaksbr(prefix_message)
                    return mark_safe(prefix_message + '<PRE>' + escape(message) + '</PRE>')
            else:
                return
    else:
        return


@admin_display(short_description='Run algorithm')
def run_algorithm(modeladmin, request, queryset):
    for algorithm_job in queryset:
        tasks.run_algorithm.delay(algorithm_job.id)


@admin_display(short_description='Run scoring')
def run_scoring(modeladmin, request, queryset):
    for score_job in queryset:
        tasks.run_scoring.delay(score_job.id)


@admin.register(models.Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creator', 'created', 'active', 'data_link')
    readonly_fields = ('data_link',)

    def data_link(self, obj):
        if obj.data:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.data.url,))
        else:
            return 'No attachment'

    data_link.allow_tags = True

    # overrride default textfield model
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'docker_image_id':
            formfield.widget = TextInput(attrs=formfield.widget.attrs)
        return formfield


@admin.register(models.AlgorithmJob)
class AlgorithmJobAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creator', 'created', 'algorithm', 'dataset', 'status')
    actions = [run_algorithm]


@admin.register(models.AlgorithmResult)
class AlgorithmResultAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'created',
        'algorithm_job',
        'algorithm',
        'dataset',
        'data_link',
        'log_link',
    )
    # lint test fail with this line?
    readonly_fields = ('data_link', 'algorithm', 'dataset', 'log_link', 'log_preview', 'result_preview',)

    def data_link(self, obj):
        if obj.data:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.data.url,))
        else:
            return 'No attachment'

    data_link.allow_tags = True

    def log_link(self, obj):
        if obj.log:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.log.url,))
        else:
            return 'No attachment'

    log_link.allow_tags = True

    def algorithm(self, obj):
        return obj.algorithm_job.algorithm

    def dataset(self, obj):
        return obj.algorithm_job.dataset

    def log_preview(self, obj):
        return _text_preview(obj.log)

    def result_preview(self, obj):
        # not show if it's None?? how to hide the column?
        return _result_preview(obj.data, obj.data_mimetype)

    # overrride default textfield model from textarea to text input
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'data_mimetype':
            formfield.widget = TextInput(attrs=formfield.widget.attrs)
        return formfield


@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creator', 'created', 'task_list', 'active', 'data_link')
    readonly_fields = ('data_link', 'task_list')

    def data_link(self, obj):
        if obj.data:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.data.url,))
        else:
            return 'No attachment'

    data_link.allow_tags = True

    def task_list(self, obj):
        return ', '.join([t.name for t in obj.tasks.all()])


@admin.register(models.Groundtruth)
class GroundtruthAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'task', 'creator', 'created', 'active', 'public', 'data_link')
    readonly_fields = ('data_link',)

    def data_link(self, obj):
        if obj.data:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.data.url,))
        else:
            return 'No attachment'

    data_link.allow_tags = True


@admin.register(models.ScoreAlgorithm)
# subclassing AlgorithmAdmin to avoid duplicate codes
class ScoreAlgorithmAdmin(AlgorithmAdmin):
    list_display = ('__str__', 'task', 'creator', 'created', 'active', 'data_link')


@admin.register(models.ScoreJob)
class ScoreJobAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'creator',
        'created',
        'score_algorithm',
        'algorithm_result',
        'groundtruth',
        'status',
    )
    actions = [run_scoring]


@admin.register(models.ScoreResult)
class ScoreResultAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'created',
        'score_job',
        'algorithm',
        'dataset',
        'algorithm_result',
        'score_algorithm',
        'groundtruth',
        'data_link',
        'log_link',
        'overall_score',
        'result_type',
    )
    readonly_fields = (
        'data_link',
        'log_link',
        'algorithm',
        'dataset',
        'algorithm_result',
        'score_algorithm',
        'groundtruth',
        'overall_score',
        'result_type',
        'log_preview',
    )

    def data_link(self, obj):
        if obj.data:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.data.url,))
        else:
            return 'No attachment'

    data_link.allow_tags = True

    def log_link(self, obj):
        if obj.log:
            return mark_safe('<a href="%s" download>Download</a>' % (obj.log.url,))
        else:
            return 'No attachment'

    log_link.allow_tags = True

    def algorithm(self, obj):
        return obj.score_job.algorithm_result.algorithm_job.algorithm

    def dataset(self, obj):
        return obj.score_job.algorithm_result.algorithm_job.dataset

    def algorithm_result(self, obj):
        return obj.score_job.algorithm_result

    def score_algorithm(self, obj):
        return obj.score_job.score_algorithm

    def groundtruth(self, obj):
        return obj.score_job.groundtruth

    def overall_score(self, obj):
        return obj.score_job.overall_score

    def result_type(self, obj):
        return obj.score_job.result_type

    def log_preview(self, obj):
        return _text_preview(obj.log)


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creator', 'created', 'active')
