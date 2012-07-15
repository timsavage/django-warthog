from django import template
from warthog.models import ContentBlock

register = template.Library()


@register.simple_tag(takes_context=True)
def content_block(context, block_name):
    try:
        cb = ContentBlock.objects.get(name=block_name)
    except ContentBlock.DoesNotExist:
        return ''

    t = template.Template(cb.published_content)
    return t.render(context)
