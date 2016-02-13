# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import template
from ..models import Resource
from ..render import render_resource

register = template.Library()


@register.simple_tag(takes_context=True)
def inline_resource(context, pk_or_path, fallback_text='Resource `{}` not found'):
    """
    Render a resource inline

    :param context: Current render context
    :param pk_or_path: An ID or path of resource to be rendered
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
        pass
    else:
        if resource.can_serve(request.user):
            return render_resource(resource, request)

    return fallback_text.format(pk_or_path)
