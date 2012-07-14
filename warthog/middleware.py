from django.conf import settings
from django.http import Http404
from warthog.views import CMS


class CmsMiddleware(object):
    """
    Middleware for capturing unhandled URI's and checks for matching content.
    """
    def __init__(self):
        self.view = CMS.as_view()

    def process_response(self, request, response):
        """
        Handle response event.

        :param request: object.
        :param response: object.

        """
        if response.status_code != 404:
            return response # No need to check for a cms resource for non-404 responses.
        try:
            return self.view(request)
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
        return response
