# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
from django.contrib.admin import widgets as admin_widgets
from django.core import validators
from django.forms import fields
from ..resource_types import uploads

# Attempt Tinymce for HTML widget
try:
    from tinymce.widgets import AdminTinyMCE as AdminHtmlWidget
except ImportError:
    AdminHtmlWidget = admin_widgets.AdminTextareaWidget


class ResourceFieldBase(object):
    label = None
    field = fields.CharField
    widget = None

    def to_database(self, value, resource, code):
        """
        Convert an internal value into a string form for storage in the database.
        :param value: The value to be converted to a string.
        :param resource: resource this item is being saved to.
        :param code: Field code this item is being saved for.
        :return:
        """
        return value

    def to_python(self, value, resource, code):
        """
        Convert a value from the database into a value for use internally and in views.
        :param value: Value from the database.
        :param resource: resource this item is being loaded from.
        :param code: Field code this item is being loaded for.
        :return:
        """
        return value

    def create_form_field(self, field_kwargs, widget_kwargs=None):
        """
        Create an instance of a form field.
        :return:
        """
        field_kwargs = field_kwargs or dict()

        if self.widget:
            widget_kwargs = widget_kwargs or dict()
            field_kwargs['widget'] = self.widget(**widget_kwargs)

        return self.field(**field_kwargs)


class CharResourceField(ResourceFieldBase):
    label = 'Text'


class TextResourceField(ResourceFieldBase):
    label = 'Text Area'
    widget = admin_widgets.AdminTextareaWidget


class BooleanResourceField(ResourceFieldBase):
    label = "Checkbox"
    field = fields.BooleanField

    def to_database(self, value, resource, code):
        return 'true' if value else 'false'

    def to_python(self, value, resource, code):
        if isinstance(value, basestring) and value.lower() in ('false', '0'):
            return False
        else:
            return bool(value)


class TemporalResourceField(ResourceFieldBase):
    def to_python(self, value, resource, code):
        if value in validators.EMPTY_VALUES:
            return None
        return self.strptime(value)

    def strptime(self, value):
        raise NotImplementedError()


class DateResourceField(TemporalResourceField):
    label = 'Date'
    field = fields.DateField
    widget = admin_widgets.AdminDateWidget

    FORMAT = '%Y-%m-%d'

    def to_database(self, value, resource, code):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.strftime(self.FORMAT)
        else:
            return None

    def strptime(self, value):
        return datetime.datetime.strptime(value, self.FORMAT).date()


class TimeResourceField(TemporalResourceField):
    label = 'Time'
    field = fields.TimeField
    widget = admin_widgets.AdminTimeWidget

    FORMAT = '%H:%M:%S'

    def to_database(self, value, resource, code):
        if isinstance(value, (datetime.time, datetime.datetime)):
            return value.strftime(self.FORMAT)
        else:
            return str(value)

    def strptime(self, value):
        return datetime.datetime.strptime(value, self.FORMAT).time()


class DateTimeResourceField(ResourceFieldBase):
    label = 'Date Time'
    field = fields.DateTimeField
    widget = admin_widgets.AdminSplitDateTime

    FORMAT = '%Y-%m-%dT%H:%M:%S'

    def to_database(self, value, resource, code):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.FORMAT)
        else:
            return str(value)

    def to_python(self, value, resource, code):
        if value in validators.EMPTY_VALUES:
            return None
        return datetime.datetime.strptime(value, self.FORMAT)


class HtmlResourceField(ResourceFieldBase):
    """
    HTML resource_types
    """
    label = "HTML"
    widget = AdminHtmlWidget


class FileResourceField(ResourceFieldBase):
    label = "File"
    field = fields.FileField
    widget = admin_widgets.AdminFileWidget

    def to_database(self, value, resource, code):
        return uploads.save_file('resource_types/%s/%s-%s' % (resource.id, code, value.name), value)

    def to_python(self, value, resource, code):
        if value:
            return uploads.as_field_file(value)


class ImageResourceField(FileResourceField):
    label = "Image"
    field = fields.ImageField
