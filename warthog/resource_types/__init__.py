# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .fields import (CharResourceField, BooleanResourceField, DateResourceField,
                     DateTimeResourceField, TextResourceField, TimeResourceField, HtmlResourceField, FileResourceField,
                     ImageResourceField)


class _Registry(object):
    def __init__(self):
        self.__default = CharResourceField()
        self.__fields = { # Pre-register internal fields.
            'char': self.__default,
            'bool': BooleanResourceField(),
            'date': DateResourceField(),
            'datetime': DateTimeResourceField(),
            'time': TimeResourceField(),
            'text': TextResourceField(),
            'html': HtmlResourceField(),
            'file': FileResourceField(),
            'image': ImageResourceField(),
        }

    def register(self, code, instance, default=False):
        if len(code) > 25:
            raise ValueError('code argument must be 25 characters or less.')
        if default:
            self.__default = instance
        self.__fields[code] = instance

    @property
    def choices(self):
        """
        Returns choice list that can be used in forms/models.
        """
        return [(k, v.label) for k, v in self.__fields.iteritems()]

    def __getitem__(self, code):
        return self.__fields.get(code, self.__default)


# Library instance.
library = _Registry()
