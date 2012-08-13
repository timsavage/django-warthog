from django import forms
from warthog.models import Resource
from warthog import fields
from warthog.admin import uploads


class ResourceFieldsForm(forms.Form):
    def __init__(self, resource_type, instance=None, *args, **kwargs):
        self.resource_type = resource_type
        super(ResourceFieldsForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})
        for field in  self.resource_type.fields.all():
            field_instance = fields.get_field_instance(field.field_type, field.get_kwargs())
            self.fields[field.code] = field_instance
            if isinstance(field_instance, forms.FileField) and field.code in initial:
                initial[field.code] = uploads.as_field_file(initial[field.code])
        self.initial = initial

    def save_to(self, obj):
        changed_data = self.changed_data
        cleaned_data = self.cleaned_data
        obj.fields.filter(code__in=changed_data).delete()
        for code, value, field in [(code, cleaned_data[code], self.fields[code]) for code in changed_data]:
            if isinstance(field, forms.FileField):
                if value:
                    obj.fields.create(code=code,
                        value=uploads.save_file('resource/%s/%s-%s' % (
                            obj.pk, code, value.name), value),
                    )
            else:
                obj.fields.create(code=code, value=value)


class ResourceAddForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('type', 'title', 'uri_path', 'parent', 'order')
        readonly = ('parent', )


