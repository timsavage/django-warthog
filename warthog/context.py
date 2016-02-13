# -*- coding: utf-8 -*-
from django.template.context import RequestContext


class CmsRequestContext(RequestContext):
    """
    Version of the request context that maintains additional information for
    requests.

    """
    def __init__(self, site, request, resource, *args, **kwargs):
        self.site = site
        self.resource = resource
        super(CmsRequestContext, self).__init__(request, *args, **kwargs)
