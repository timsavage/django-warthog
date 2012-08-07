from django import forms
from warthog.models import Resource
from warthog import fields
from warthog.admin import uploads


class ResourceFieldsForm(forms.Form):
    def __init__(self, resource_type, *args, **kwargs):
        self.resource_type = resource_type
        super(ResourceFieldsForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})
        for field in  self.resource_type.fields.all():
            field_instance = fields.get_field_instance(field.field_type, field.get_kwargs())
            self.fields[field.code] = field_instance
            if isinstance(field_instance, forms.FileField) and field.code in initial:
                initial[field.code] = uploads.as_field_file(initial[field.code])
        self.initial = initial


class ResourceAddForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('type', 'title', 'uri_path', 'parent', 'order')

