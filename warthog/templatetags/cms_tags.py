from django import template
from warthog.models import Resource, ResourceType
from warthog.data_structures import ResourceIterator

register = template.Library()


@register.assignment_tag
def get_resource(pk):
    """Get a resource from it's ID."""
    try:
        return Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        return None


@register.assignment_tag
def get_resource_type(code, include_hidden=False):
    resource_type = ResourceType.objects.get(code=code)
    return ResourceIterator.for_type(resource_type, include_hidden)


@register.assignment_tag(takes_context=True)
def get_children(context, resource=None, include_hidden=False):
    return ResourceIterator.for_children(resource or context.resource, include_hidden)
