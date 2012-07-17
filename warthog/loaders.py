from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from warthog.models import Template


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
