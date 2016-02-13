# -*- coding: utf-8 -*-
from models import Resource

# TODO: A lot of opportunity here for caching


class ResourceItemFields(object):
    """
    Wrapper around resource item fields
    """
    __slots__ = ('__field_map', )

    def __init__(self, fields):
        field_lookup = {}
        for field in fields:
            field_lookup[field.code] = field.value
        self.__field_map = field_lookup

    def __getitem__(self, item):
        return self.__field_map[item]


class ResourceItem(object):
    """
    Wrapper around resource item
    """
    def __init__(self, resource):
        self.resource = resource
        self.vars = ResourceItemFields(resource.fields.all())

    @property
    def title(self):
        return self.resource.title

    @property
    def menu_title(self):
        return self.resource.menu_title

    @property
    def menu_class(self):
        return self.resource.menu_class

    @property
    def uri_path(self):
        return self.resource.uri_path


class ResourceIterator(object):
    """
    Resource iterator for iterating over resource query sets
    """
    def __init__(self, queryset):
        self.resources = queryset

    @classmethod
    def for_type(cls, resource_type, include_hidden=False):
        """
        Get a resource iterator for a particular resource type.
        :param resource_type: Resource type object.
        :return:
        """
        queryset = Resource.objects.all()
        if not include_hidden:
            queryset = queryset.filter(hide_from_menu=False)
        return cls(queryset)

    @classmethod
    def for_children(cls, resource, include_hidden=False):
        """
        Get a resource iterator for child objects.
        :param cls:
        :param resource:
        :return:
        """
        queryset = resource.children.all()
        if not include_hidden:
            queryset = queryset.filter(hide_from_menu=False)
        return cls(queryset)

    def __iter__(self):
        for resource in self.resources:
            if resource.is_live:
                yield ResourceItem(resource)

    def __len__(self):
        return len(self.resources)
