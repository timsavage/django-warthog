# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.core.cache import cache


def generate_cache_key(instance_or_type, **vary_by):
    """Generate a cache key for a model object."""
    opts = instance_or_type._meta
    return 'model:{}[{}]'.format(
        opts.db_table,
        ','.join(['%s=%s' % v for v in vary_by.iteritems()])
    )


class CachingManager(models.Manager):
    """Manager that handles caching transparently."""
    def get_queryset(self):
        return CachingQuerySet(self.model)

    def contribute_to_class(self, model, name):
        models.signals.post_save.connect(self._post_save, sender=model)
        models.signals.post_delete.connect(self._post_save, sender=model)
        setattr(model, 'generate_cache_key', classmethod(generate_cache_key))
        setattr(model, 'cache_key', property(lambda self: self.generate_cache_key(pk=self.pk)))
        return super(CachingManager, self).contribute_to_class(model, name)

    def _invalidate_cache(self, instance):
        """
        Explicitly set a None value instead of just deleting so we don't have any race
        conditions where:
            Thread 1 -> Cache miss, get object from DB
            Thread 2 -> Object saved, deleted from cache
            Thread 1 -> Store (stale) object fetched from DB in cache
        Five second should be more than enough time to prevent this from happening for
        a web app.
        """
        cache.set(instance.cache_key, None, 5)

    def _post_save(self, instance, **kwargs):
        self._invalidate_cache(instance)

    def _post_delete(self, instance, **kwargs):
        self._invalidate_cache(instance)


class CachingQuerySet(QuerySet):
    def iterator(self):
        super_iterator = super(CachingQuerySet, self).iterator()
        while True:
            obj = super_iterator.next()
            # Use cache.add instead of cache.set to prevent race conditions (see CachingManager)
            cache.add(obj.cache_key, obj)
            yield obj

    def get(self, *args, **kwargs):
        """
        Checks the cache to see if there's a cached entry for this pk. If not, fetches
        using super then stores the result in cache.

        Most of the logic here was gathered from a careful reading of
        ``django.db.models.sql.query.add_filter``
        """
        # Punt on anything more complicated than get by pk/id only...
        # If there is any other ``where`` filter on this QuerySet just call
        # super. There will be a where clause if this QuerySet has already
        # been filtered/cloned.
        if not self.query.where and len(kwargs) == 1:
            k = kwargs.keys()[0]
            if k in ('pk', 'pk__exact', '%s' % self.model._meta.pk.attname,
                     '%s__exact' % self.model._meta.pk.attname):
                obj = cache.get(self.model.generate_cache_key(pk=kwargs[k]))
                if obj is not None:
                    obj.from_cache = True
                    return obj

        # Calls self.iterator to fetch objects, storing object in cache.
        return super(CachingQuerySet, self).get(*args, **kwargs)


class ResourceTypeManager(CachingManager):
    """Manager for resource type objects"""
    def get_queryset(self):
        return super(ResourceTypeManager, self).get_queryset()


class ResourceManager(CachingManager):
    """Manager for dealing with resource models."""
    use_for_related_fields = True

    def get_queryset(self):
        return super(ResourceManager, self).get_queryset()

    def get_front(self, **filters):
        """
        Apply default filters for getting an item for front display.

        By default applies published=True, delete=False, site=settings.SITE_ID

        :param filters: additional filters to apply
        :return: Resource
        """
        filters.update(published=True, deleted=False, site=settings.SITE_ID)
        return self.get(**filters)

    def filter_front(self, **filters):
        """
        Apply default filters for front display of items.

        By default applies published=True, delete=False, site=settings.SITE_ID

        :param filters: additional filters to apply
        :return: Queryset
        """
        filters.update(published=True, deleted=False, site=settings.SITE_ID)
        return self.filter(**filters)

    def get_uri_path(self, uri_path):
        """
        Get a resource from the URI path.

        :param uri_path: path to search for.

        """
        # Normalise path
        if len(uri_path) > 1 and uri_path.endswith('/'):
            uri_path = uri_path[:-1]

        # Try to get from cache
        ref_key = generate_cache_key(self.model, uri_path=uri_path)
        cache_key = cache.get(ref_key) if ref_key else None
        resource = cache.get(cache_key) if cache_key else None

        if not resource:
            resource = self.get_front(uri_path__exact=uri_path)

            cache_key = generate_cache_key(self.model, pk=resource.pk)
            cache.set(cache_key, resource)
            cache.set(ref_key, cache_key)
        return resource
