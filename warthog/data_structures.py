from models import Resource

#TODO: A lot of opportunity here for caching

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
        self.queryset = queryset

    @classmethod
    def for_type(cls, resource_type):
        """
        Get a resource iterator for a particular resource type.
        :param resource_type: Resource type object.
        :return:
        """
        return cls(Resource.objects.filter(type_id=resource_type.id))

    @classmethod
    def for_children(cls, resource):
        """
        Get a resource iterator for child objects.
        :param cls:
        :param resource:
        :return:
        """
        return cls(resource.children.all())

    def __iter__(self):
        for resource in self.queryset:
            yield ResourceItem(resource)
