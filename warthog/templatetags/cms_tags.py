from django import template
from warthog.models import Resource, ContentBlock

register = template.Library()


@register.simple_tag(takes_context=True)
def content_block(context, block_name):
    """Load a content block and render.

    :param block_name: Name of the block to load.

    """
    try:
        cb = ContentBlock.objects.get(name=block_name)
    except ContentBlock.DoesNotExist:
        return ''

    t = template.Template(cb.published_content)
    return t.render(context)


@register.assignment_tag(takes_context=True)
def parent_resource(context, resource=None):
    """Get parent resource of the current resource."""
    resource = resource or context.resource
    return resource.parent


@register.assignment_tag(takes_context=True)
def child_resources(context, resource=None):
    """Get children of the current resource."""
    resource = resource or context.resource
    return resource.children.all()


@register.assignment_tag
def resource_by_id(pk):
    """Get a resource from it's ID."""
    try:
        return Resource.objects.get_id(pk)
    except Resource.DoesNotExist:
        return None

