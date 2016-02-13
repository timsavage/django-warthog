# -*- coding: utf-8 -*-


class LazySettings(object):
    def _load_settings(self):
        from warthog import default_settings
        from django.conf import settings as django_settings

        for key in dir(default_settings):
            if not key.startswith('CMS_'):
                continue

            setattr(self, key, getattr(django_settings, key,
                getattr(default_settings, key)))

    def __getattr__(self, attr):
        self._load_settings()
        del self.__class__.__getattr__
        return self.__dict__[attr]
settings = LazySettings()
