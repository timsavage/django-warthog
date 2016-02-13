# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import forms
from ..models import Resource
from ..resource_types import library


class ResourceFieldsForm(forms.Form):
    """
    Form that dynamically creates form fields based on a ResourceType definition.
    """
    def __init__(self, resource_type, instance, *args, **kwargs):
        self.resource_type = resource_type
        self.instance = instance
        super(ResourceFieldsForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})
        for f in resource_type.fields.all():
            self.fields[f.code] = f.create_form_field()
            initial[f.code] = library[f.field_type].to_python(initial.get(f.code), instance.pk, f.code)
        self.initial = initial

    def save_to(self, obj):
        """
        Save the values on this form to a resource_types object.
        :param obj: ResourceObject to save form fields to.
        """
        changed_data = self.changed_data
        cleaned_data = self.cleaned_data
        obj.fields.filter(code__in=changed_data).delete()
        for code, value in ((code, cleaned_data[code]) for code in changed_data):
            obj.fields.create(code=code, value=library[code].to_database(value, obj.pk, code))


class ResourceAddForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('site', 'type', 'title', 'slug', 'parent', 'order')
        readonly = ('parent', )
