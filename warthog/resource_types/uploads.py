# -*- coding: utf-8 -*-
from django.core.files.base import File
from django.core.files.storage import DefaultStorage


storage = DefaultStorage()


def save_file(name, uploaded_file):
    return storage.save(name, uploaded_file)


class FieldFile(File):
    def __init__(self, name, storage):
        super(FieldFile, self).__init__(None, name)
        self.storage = storage

    def __eq__(self, other):
        # Older code may be expecting FileField values to be simple strings.
        # By overriding the == operator, it can remain backwards compatibility.
        if hasattr(other, 'name'):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # Required because we defined a custom __eq__.
        return hash(self.name)

    def _get_file(self):
        if not hasattr(self, '_file') or self._file is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def _get_path(self):
        return self.storage.path(self.name)
    path = property(_get_path)

    def _get_url(self):
        return self.storage.url(self.name)
    url = property(_get_url)


def as_field_file(name):
    return FieldFile(name, storage)
