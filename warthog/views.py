# -*- coding: utf-8 -*-
from logging import getLogger
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .models import Resource
from .render import render_resource


logger = getLogger('warthog.views')


class Cms(View):
    """View for displaying CMS resources.

    **Example**::

        from django.conf.urls import *
        from warthog.views import Cms

        urlpatterns = patterns('',
            url(r'^content/', Cms.as_view()),
        )

    The ``as_view`` method takes a several options:

    ``superuser_view_all``
        ``bool`` value to indicate that users with the ``is_superuser`` flag
        can view all pages including those which have not been published or
        are outside the published date range. **Default:** ``True``
    ``permission``
        Name of a permission that gives a user the ability to view all pages
        including those which have not been published or are outside the
        published date range. **Default:** ``preview_resource``

    .. note::
        This view is also used by :ref:CMSMiddleware to handle page requests.

    """
    def load_resource(self, *args, **kwargs):
        """Load the actual resource."""
        try:
            return Resource.objects.get_uri_path(self.request.path_info)
        except Resource.DoesNotExist:
            raise Http404

    @property
    def can_serve_flags(self):
        try:
            return self._can_serve_flags
        except AttributeError:
            flags = {}
            if hasattr(self, 'superuser_view_all'):
                flags['allow_superuser'] = getattr(self, 'superuser_view_all')
            if hasattr(self, 'permission'):
                flags['permission'] = getattr(self, 'permission')
            self._can_serve_flags = flags
            return flags

    def get(self, request, *args, **kwargs):
        """Respond to ``get`` HTTP method."""
        resource = self.load_resource(*args, **kwargs)

        if not resource.can_serve(request.user, **self.can_serve_flags):
            raise Http404

        return HttpResponse(render_resource(resource, request))


class CmsPreview(Cms):
    """View for previewing CMS resources.

    **Example**::

        from django.conf.urls import *
        from warthog.views import CmsPreview

        urlpatterns = patterns('',
            url(r'^preview/(\d+)/$', CmsPreview.as_view()),
        )

    The ``as_view`` method takes a several options:

    ``superuser_view_all``
        ``bool`` value to indicate that users with the ``is_superuser`` flag
        can view all pages including those which have not been published or
        are outside the published date range. **Default:** ``True``
    ``permission``
        Name of a permission that gives a user the ability to view all pages
        including those which have not been published or are outside the
        published date range. **Default:** ``preview_resource``

    """
    def load_resource(self, resource_id):
        return get_object_or_404(Resource, pk=resource_id)
