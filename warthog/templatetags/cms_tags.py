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


@register.assignment_tag
def get_resource(pk):
    """Get a resource from it's ID."""
    try:
        return Resource.objects.get_id(pk)
    except Resource.DoesNotExist:
        return None

