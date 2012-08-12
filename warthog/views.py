from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.template import Template, loader
from django.utils.log import getLogger
from django.utils.safestring import mark_safe
from django.views.generic import View
from warthog.context import CmsRequestContext
from warthog.models import Resource


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

    def can_serve(self, resource):
        """Determine if this resource can be served."""
        if resource.is_live:
            return True

        user = self.request.user
        if getattr(self, 'superuser_view_all', True) and user.is_superuser:
            return True

        permission = getattr(self, 'permission', 'preview_resource')
        if permission and user.has_perm(permission):
            return True

        return False

    def render(self, resource):
        """Handle rendering of the resource."""

        # Build up rendering context
        params = dict([(r.code, mark_safe(r.value)) for r in resource.fields.all()])
        params['title'] = resource.title

        context = CmsRequestContext(self.request, resource, params)

        template = loader.get_template(resource.type.default_template)
        return HttpResponse(template.render(context))#, mimetype=template.mime_type)

    def get(self, request, *args, **kwargs):
        """Respond to ``get`` HTTP method."""
        resource = self.load_resource(*args, **kwargs)

        if not self.can_serve(resource):
            raise Http404

        return self.render(resource)


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
