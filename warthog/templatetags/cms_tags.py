# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import template
from ..models import Resource, ResourceType
from ..data_structures import ResourceIterator, ResourceItem

register = template.Library()


@register.assignment_tag
def get_resource(pk_or_path):
    """
    Get a resource from it's ID or path.
    """
    try:
        filters = dict(pk=int(pk_or_path))
    except ValueError:
        # Assume is path
        filters = dict(uri_path=pk_or_path)

    try:
        resource = Resource.objects.get_front(**filters)
    except Resource.DoesNotExist:
        return None
    else:
        if resource.is_live:
            return ResourceItem(resource)


@register.assignment_tag
def get_resource_type(code, include_hidden=False):
    resource_type = ResourceType.objects.get(code=code)
    return ResourceIterator.for_type(resource_type, include_hidden)


@register.assignment_tag(takes_context=True)
def get_children(context, resource=None, include_hidden=False):
    if isinstance(resource, int):
        resource = get_resource(resource)
    elif resource is None:
        resource = context.resource
    return ResourceIterator.for_children(resource, include_hidden)
