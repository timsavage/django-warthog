# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import template
from ..models import Resource
from ..render import render_resource

register = template.Library()


@register.simple_tag(takes_context=True)
def inline_resource(context, pk_or_path, not_found='Resource `{}` not found'):
    """
    Render a resource inline

    :param context: Current render context
    :param pk_or_path: An ID or path of resource to be rendered
    :param not_found: Text to display if resource is not found.
    """
    try:
        request = context['request']
    except KeyError:
        raise KeyError('The request object is required to be part of the context. '
                       'Add "django.core.context_processors.request" to your TEMPLATE_CONTEXT_PROCESSORS setting')

    try:
        filters = dict(pk=int(pk_or_path))
    except ValueError:
        # Assume is path
        filters = dict(uri_path=pk_or_path)

    try:
        resource = Resource.objects.get_front(**filters)
    except Resource.DoesNotExist:
        return not_found.format(pk_or_path)
    else:
        if resource.can_serve(request.user):
            return render_resource(resource, request)

    return ''  # Return empty text if user permissions don't pass
