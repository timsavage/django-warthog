from django.forms import fields
from django.forms import widgets
from django.contrib.admin import widgets as admin_widgets

DEFAULT_FIELD = (
    'Character field',
    fields.CharField,
    None
)


# Registered list of fields (with defaults)
__resource_fields = {
    'char': DEFAULT_FIELD,
    'text': (
        'Text area',
        fields.CharField,
        admin_widgets.AdminTextareaWidget
    ),
    'bool': (
        'Boolean field',
        fields.BooleanField,
        None
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


def remove(code):
    """Remove a resource field.

    .. note:
        Care must be taken when choosing to remove a resource field that is in
        use.

    :param code: Code of the resource to remove.

    """
    __resource_fields.pop(code)


def get_field_choices():
    """Generate a choices list of for using in models.

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
    pass
else:
    register('html', 'HTML Field', fields.CharField, AdminTinyMCE)
