~~~~~~~~~~~~~~
Django Warthog
~~~~~~~~~~~~~~

Simple embeddable CMS for Django. Supports for:

- addition of CMS pages
- embedded content blocks
- scheduled (un)publishing of content
- handling of multiple sites (via Django sites framework)
- management of templates

============
Installation
============

Add warthog to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'warthog',
        ...
    )

Add the warthog middleware into the MIDDLEWARE_CLASSES::

    MIDDLEWARE_CLASSES = (
        ...
        'warthog.middleware.CmsMiddleware',
        ...
    )

Enable template loaders for customising any template::

    # For Django 1.8+
    TEMPLATES = (
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'loaders': (
                    'django.template.loaders.app_directories.Loader',
                    'warthog.loaders.CmsTemplateLoader',
                )
            }
        }
    )
