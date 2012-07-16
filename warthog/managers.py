from django.db import models


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
#        reference_key = _cache_key(self.model, url, 'url_alias')
#        resource = get_item_by_reference(reference_key)
#        if resource:
#            return resource

        # Query item
        resource = self.select_related('resource_variables').get(uri_path__exact=uri_path, published=True, deleted=False)

        # Cache item if one is found
#        if resource:
#            item_key = resource.cache_key
#            cache.add(item_key, resource, CACHE_DURATION)
#            cache.add(reference_key, item_key, CACHE_DURATION)

        return resource

    def get_id(self, id):
        # Query item
        resource = self.select_related('resource_variables').get(id=id, published=True, deleted=False)

        return resource
