# -*- coding: utf-8 -*-
from django.apps import AppConfig


class WarthogAppConfig(AppConfig):
    name = 'warthog'
    verbose_name = 'Warthog CMS'


default_app_config = 'warthog.WarthogAppConfig'

VERSION = (0, 4, 2, 'beta')
__version__ = '.'.join(map(str, VERSION))
