import logging
import datetime
from django.forms import fields
from django.forms import widgets
from django.core import validators
from django.contrib.admin import widgets as admin_widgets


class ResourceFieldRegistry(object):
    def __init__(self):
        self.__registry = {}

    def register(self, code):
        assert isinstance(code, basestring)
        def wrapper(klass):
            self.__registry[code] = klass()
        return wrapper

resource_fields = ResourceFieldRegistry()


class ResourceFieldBase(object):
    label = None
    field = fields.CharField
    widget = None

    def to_database(self, value):
        """
        Convert an internal value into a string form for storage in the database.
        :param value: The value to be converted to a string.
        :return:
        """
        return value

    def to_python(self, value):
        """
        Convert a value from the database into a value for use internally and in views.
        :param str_value: Value from the database.
        :return:
        """
        return value

    def create_form_field(self, field_kwargs, widget_kwargs):
        """
        Create an instance of a form field.
        :return:
        """
        field_kwargs = field_kwargs or dict()
        field_kwargs.update({'label': self.label})

        if self.widget:
            widget_kwargs = field_kwargs or dict()
            field_kwargs['widget'] = self.widget(**widget_kwargs)

        return self.field(**field_kwargs)


@resource_fields.register('char')
class CharResourceField(ResourceFieldBase):
    label = 'Text Field'


@resource_fields.register('text')
class TextResourceField(ResourceFieldBase):
    label = 'Text Area'
    widget = admin_widgets.AdminTextareaWidget


@resource_fields.register('bool')
class BooleanResourceField(ResourceFieldBase):
    label = "Checkbox"
    field = fields.BooleanField

    def to_database(self, value):
        return 'true' if value else 'false'

    def to_python(self, value):
        if isinstance(value, basestring) and value.lower() in ('false', '0'):
            return False
        else:
            return bool(value)


class TemporalResourceField(ResourceFieldBase):
    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        return self.strptime(value)

    def strptime(self, value):
        raise NotImplementedError()


@resource_fields.register('date')
class DateResourceField(TemporalResourceField):
    label = 'Date'
    field = fields.DateField
    widget = admin_widgets.AdminDateWidget

    FORMAT = '%Y-%m-%d'

    def to_database(self, value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.strftime(self.FORMAT)
        else:
            return None

    def strptime(self, value):
        return datetime.datetime.strptime(value, self.FORMAT).date()


@resource_fields.register('time')
class TimeResource(TemporalResourceField):
    label = 'Time'
    field = fields.TimeField
    widget = admin_widgets.AdminTimeWidget

    FORMAT = '%H:%M:%S'

    def to_database(self, value):
        if isinstance(value, (datetime.time, datetime.datetime)):
            return value.strftime(self.FORMAT)
        else:
            return str(value)

    def strptime(self, value):
        return datetime.datetime.strptime(value, self.FORMAT).time()


@resource_fields.register('datetime')
class DateTimeResource(ResourceFieldBase):
    label = 'Date Time'
    field = fields.DateTimeField
    widget = admin_widgets.AdminSplitDateTime

    FORMAT = '%Y-%m-%dT%H:%M:%S'

    def to_database(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.FORMAT)
        else:
            return str(value)

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        return datetime.datetime.strptime(value, self.FORMAT)

DEFAULT_FIELD = (
    'Character field',
    fields.CharField,
    None, # Widget
)


log = logging.getLogger('warthog.fields')


# Registered list of fields (with defaults)
__resource_fields = {
    'char': DEFAULT_FIELD,
    'text': (
        'Text area',
        fields.CharField,
        admin_widgets.AdminTextareaWidget,
    ),
    'bool': (
        'Boolean field',
        fields.BooleanField,
        None,
    ),
    'date': (
        'Date field',
        fields.DateField,
        admin_widgets.AdminDateWidget,
    ),
    'datetime': (
        'Date/Time field',
        fields.DateTimeField,
        admin_widgets.AdminSplitDateTime,
    ),
    'file': (
        'File field',
        fields.FileField,
        admin_widgets.AdminFileWidget,
    ),
    'image': (
        'Image field',
        fields.ImageField,
        admin_widgets.AdminFileWidget,
    )
}


def register(code, label, field, widget=None):
    """Register a resource field with warthog.

    Warthog uses standard Django form fields and widgets to define resource
    fields. Additional resource fields can be registered with this method.

    .. note:
        If you want to override a default field specify a code that is already
        in use.

    :param code: Code used to reference this field type in the database. Using
        a code that is already in use will override the existing code. This
        value must be 25 characters or less as it is stored in the database.
    :param label: Label of the field used for display purposes.
    :param field: ``Field`` type used to validate/parse values.
    :param widget: Optional ``Widget`` used in admin interface for interacting
        with field.

    """
    if len(code) > 25:
        raise ValueError('"code" argument must be 25 characters or less.')
    __resource_fields[code] = (label, field, widget)
    log.info("Registered resource field `%s` as: %s", label, code)


def remove(code):
    """Remove a resource field.

    .. note:
        Care must be taken when choosing to remove a resource field that is in
        use.

    :param code: Code of the resource to remove.

    """
    __resource_fields.pop(code)
    log.info("Removed resource field: %s", code)


def get_field_choices():
    """Generate a choices list of resource names for using in models.

    :return: [(code, label), ...]
    """
    for code, (label, _, _) in __resource_fields.iteritems():
        yield code, label


def get_field_instance(code, field_kwargs=None, widget_kwargs=None):
    """Create a field instance from a code.

    .. note:
        If the code is not found a default character field will be created.

    :param code: Code of the field to create an instance of.
    :param field_kwargs: kwargs for creating the field.
    :param widget_kwargs: widget kwargs.
    :return: New field instance.
    """
    label, field, widget = __resource_fields.get(code, DEFAULT_FIELD)

    field_kwargs = {'label': label} if field_kwargs is None else field_kwargs
    widget_kwargs = {} if widget_kwargs is None else widget_kwargs

    if widget is not None:
        field_kwargs['widget'] = widget(**widget_kwargs)

    return field(**field_kwargs)



# Try to load TINY MCE
try:
    from tinymce.widgets import AdminTinyMCE
except ImportError:
    register('html', 'HTML Field', fields.CharField, admin_widgets.AdminTextareaWidget)
else:
    register('html', 'HTML Field', fields.CharField, AdminTinyMCE)
