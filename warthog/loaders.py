# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.template import TemplateDoesNotExist
from .models import Template

try:
    from django.template.loaders.base import Loader as BaseLoader
except ImportError:
    from django.template.loader import BaseLoader


class CmsTemplateLoader(BaseLoader):
    """Load templates from CMS template store"""
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        display_name = 'warthog:%s' % template_name
        try:
            template = Template.objects.get(name__exact=template_name)
            return template.content, display_name
        except Template.DoesNotExist:
            pass
        raise TemplateDoesNotExist(template_name)
