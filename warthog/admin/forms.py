from django import forms
from warthog import fields


class ResourceFieldsForm(forms.Form):
    def __init__(self, resource_type, *args, **kwargs):
        self.resource_type = resource_type
        super(ResourceFieldsForm, self).__init__(*args, **kwargs)

        for field in  self.resource_type.fields.all():
            self.fields[field.code] = fields.get_field_instance(field.field_type, field.get_kwargs())
