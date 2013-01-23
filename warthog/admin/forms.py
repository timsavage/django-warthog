from django import forms
from warthog.models import Resource
from warthog import templatevars
from warthog.admin import uploads


class ResourceFieldsForm(forms.Form):
    """
    Form that dynamically creates form fields based on a ResourceType definition.
    """
    def __init__(self, resource_type, instance=None, *args, **kwargs):
        self.resource_type = resource_type
        super(ResourceFieldsForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})
        for field in self.resource_type.fields.all():
            field_instance = templatevars.library[field.field_type].create_form_field(field.get_kwargs())
            self.fields[field.code] = field_instance
            if isinstance(field_instance, forms.FileField) and field.code in initial:
                initial[field.code] = uploads.as_field_file(initial[field.code])
        self.initial = initial

    def save_to(self, obj):
        """
        Save the values on this form to a resource object.
        :param obj: ResourceObject to save form fields to.
        """
        changed_data = self.changed_data
        cleaned_data = self.cleaned_data
        obj.fields.filter(code__in=changed_data).delete()
        for code, value in ((code, cleaned_data[code]) for code in changed_data):
            obj.fields.create(code=code, value=templatevars.library[code].to_database(value))

#            if isinstance(field, forms.FileField):
#                if value:
#                    obj.fields.create(code=code,
#                        value=uploads.save_file('resource/%s/%s-%s' % (
#                            obj.pk, code, value.name), value),
#                    )
#            else:
#                obj.fields.create(code=code, value=value)


class ResourceAddForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('type', 'title', 'slug', 'parent', 'order')
        readonly = ('parent', )
