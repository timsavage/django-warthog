# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.safestring import mark_safe
from .context import CmsRequestContext


def render_resource(resource, request):
    """
    Render a resource.

    :param resource: Resource to render
    :param request: Current request object.

    """
    site = get_current_site(request)

    # Build up rendering context
    params = {r.code: mark_safe(r.value) for r in resource.fields.all()}
    params['title'] = resource.title

    context = CmsRequestContext(site, request, resource, params)

    # Identify and load template
    template = loader.select_template([
        "%s/%s" % (site.domain, resource.type.default_template),
        resource.type.default_template
    ])

    # Render
    return template.render(context)
