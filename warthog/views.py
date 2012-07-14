from django.utils.log import getLogger
from django.views.generic import View


logger = getLogger('warthog.views')


class CMS(View):
    """
    View for designating a section of URL as CMS controlled.

    **Example**::

        from django.conf.urls import *
        from warthog.views import CMS

        urlpatterns = patterns('',
            url(r'^content/', CMS.as_view()),
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
    #``language``
    #    Override that forces all pages to be in a particular language.

    """
    def get(self, request):
        pass

