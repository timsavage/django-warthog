~~~~~~~~~~~~~~
Django Warthog
~~~~~~~~~~~~~~

Simple embeddable CMS for Django.

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
