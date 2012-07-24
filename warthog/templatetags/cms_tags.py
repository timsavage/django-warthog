from django import template
from warthog.models import Resource

register = template.Library()


@register.assignment_tag
def get_resource(pk):
    """Get a resource from it's ID."""
    try:
        return Resource.objects.get_id(pk)
    except Resource.DoesNotExist:
        return None

