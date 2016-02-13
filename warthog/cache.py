# -*- coding: utf-8 -*-
from django.core.cache import cache as default_cache


def generate_obj_key(instance_or_type, **vary_by):
    """Generate a cache key for a model object."""
    opts = instance_or_type._meta
    return 'model:%s.%s[%s]' % (
        opts.app_label, opts.module_name,
        ','.join(['%s=%s' % v for v in vary_by.iteritems()])
    )


def set_model(model_instance, cache=None):
    """
    Store a model in cache.
    
    :param model_instance: the model object to store.
    :param cache: cache instance to use; defaults to main django cache.
    :returns: cache key.
    
    """
    cache = cache or default_cache
    key = generate_obj_key(model_instance, pk=model_instance.pk)
    cache.set(key, model_instance)
    return key


def get_model(model_type, pk, cache=None):
    """Store a model in cache.
    
    :param model_type: model type for building cache key.
    :param pk: primary key of model to fetch from cache.
    :param cache: cache instance to use; defaults to main django cache.
    :returns: model object if found; else None.
    
    """
    cache = cache or default_cache
    key = generate_obj_key(model_type, pk=pk)
    return cache.get(key)


def clear_model(model_instance, cache=None):
    """Clear a model instance from cache.

    :param model_instance: the model object to store.
    :param cache: cache instance to use; defaults to main django cache.

    """
    cache = cache or default_cache
    key = generate_obj_key(model_instance, pk=model_instance.pk)
    return cache.delete(key)


def set_model_by_attribute(model_instance, attr_name, cache=None):
    """Store a model in cache by attribute value.
    
    :param model_instance: the model object to store.
    :param attr_name: attribute name.
    :param cache: cache instance to use; defaults to main django cache.
    :returns: reference cache key.
    
    .. note::
        Attribute must be unique.

    """
    cache = cache or default_cache
    # TODO: Add check for uniqueness (use unique flag)
    value = getattr(model_instance, attr_name)
    reference_key = generate_obj_key(model_instance, **{attr_name: value})
    key = set_model(model_instance, cache)
    cache.set(reference_key, key)
    return reference_key


def get_model_by_attribute(model_type, attr_name, value, cache=None):
    """Get a model from cache by reference.
    
    :param model_type: model type for building cache key.
    :param attr_name: attribute name.
    :param value: value of attribute.
    :param cache: cache instance to use; defaults to main django cache.
    :returns: model object if found; else None.

    """
    cache = cache or default_cache
    reference_key = generate_obj_key(model_type, **{attr_name: value})
    key = cache.get(reference_key)
    if key:
        return cache.get(key)
    else:
        return None
