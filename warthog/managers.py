from django.db import models
from warthog import cache


class ResourceManager(models.Manager):
    """
    Manager for dealing with resource models.
    """
    def get_uri_path(self, uri_path):
        """
        Get a resource from the URI path.

        :param uri_path: path to search for.

        """
        # Normalise path
        if len(uri_path) > 1 and uri_path.endswith('/'):
            url = uri_path[:-1]

        # Try to get from cache
        resource = cache.get_model_by_attribute(self.model, 'uri_path', uri_path)
        if resource:
            return resource

        # Query item
        resource = self.select_related('resource_variables').get(uri_path__exact=uri_path, published=True, deleted=False)

        # Cache item if one is found
        if resource:
            cache.set_model_by_attribute(resource, 'uri_path')
        return resource

    def get_id(self, id):
        # Query item
        resource = self.select_related('resource_variables').get(id=id, published=True, deleted=False)

        return resource
