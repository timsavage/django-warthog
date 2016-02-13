# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.http import Http404
from .views import Cms


class CmsMiddleware(object):
    """
    Middleware for capturing unhandled URI's and loading matching content.

    """
    def __init__(self):
        self.view = Cms.as_view()

    def process_response(self, request, response):
        """
        Handle response event.

        :param request: object.
        :param response: object.

        """
        # No need to check for a cms resource for non-404 responses.
        if response.status_code == 404:
            try:
                return self.view(request)
            except Http404:
                pass
        return response
