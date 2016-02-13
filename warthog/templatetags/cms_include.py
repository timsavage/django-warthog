# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import template
from ..models import Resource
from ..render import render_resource

register = template.Library()


@register.simple_tag(takes_context=True)
def render_resource(context, pk_or_path):
    """
    Render a resource inline
    """
    try:
        request = context.request
    except AttributeError:
        raise AttributeError('The request object is required to be part of the context. '
                             'Add "django.core.context_processors.request" to your TEMPLATE_CONTEXT_PROCESSORS setting')

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
        if resource.can_serve(request.user):
            return render_resource(resource, request)
