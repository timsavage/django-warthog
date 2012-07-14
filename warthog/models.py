from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from warthog.managers import ResourceManager


class Template(models.Model):
    """
    Defines a template.

    A template is used as the scaffolding for a page (or section of a page).

    Variables can be used within a template to define additional data items
    to be used when rendering the page.
    """
    # Description
    name = models.CharField(_('name'), db_index=True, unique=True, max_length=100)
    description = models.CharField(_('description'), blank=True, max_length=250,
        help_text=_("Optional description of template."))
    # Options
    cacheable = models.BooleanField(_('cachable'), default=True)
    # Content
    content = models.TextField(_('content'))
    # Tracking
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ['name', ]

    def __unicode__(self):
        return self.name


class ContentBlock(models.Model):
    """
    Defines a content block.
    """
    # Description
    name = models.CharField(_('name'), db_index=True, unique=True, max_length=100)
    description = models.CharField(_('description'), blank=True, max_length=250,
        help_text=_("Optional description of content block."))
    # Options
    cacheable = models.BooleanField(_('cacheable'), default=False,
        help_text=_("Is the generated content cacheable."))
    # Content
    content = models.TextField(_('content'), null=True, blank=True)
    # Tracking
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        verbose_name = _('content block')
        verbose_name_plural = _('content blocks')
        ordering = ['name', ]

    def __unicode__(self):
        return self.name


class Resource(models.Model):
    """
    CMS Resource model, resource that is served on a particular URI.
    """

    RESOURCE_TYPES = (
        ('content', _('Content')),
        ('link',    _('Link')),
    )

    MIME_TYPES = (
        ('Text (text/*)', (
            ('text/html',          _('HTML')),
            ('text/plain',         _('Text')),
            ('text/css',           _('CSS')),
            ('text/javascript',    _('JavaScript')),
            ('text/csv',           _('CSV')),
            ('text/xml',           _('XML')),
            ('text/cachemanifest', _('HTML5 Cache Manifest')),
        )),
        ('Application (application/*)', (
            ('application/xhtml+xml',  _('XHTML')),
            ('application/javascript', _('JavaScript')),
            ('application/json',       _('JSON')),
        ))
    )

    CONTENT_DISPOSITIONS = (
        ('',           _('None')),
        ('inline',     _('Inline')),
        ('attachment', _('Attachment'))
    )

    # Statuses of the resource
    STATUS_DELETED = 0
    STATUS_UNPUBLISHED = 1
    STATUS_EXPIRED = 2
    STATUS_SCHEDULED = 3
    STATUS_LIVE = 4

    STATUS_EXPANDED = {
        STATUS_DELETED: ('deleted', _('Deleted'), _('This resources has been deleted.')),
        STATUS_UNPUBLISHED: ('unpublished', _('Unpublished'), _('This resource has not been published.')),
        STATUS_EXPIRED: ('expired', _('Expired'), _('This resource has expired (un-publish date is in the past).')),
        STATUS_SCHEDULED: ('scheduled', _('Scheduled'), _('This resource is scheduled to be published (publish date is in the future).')),
        STATUS_LIVE: ('live', _('Live'), _('This resource is live.')),
    }

    # Description
    title = models.CharField(_('title'), max_length=100,
        help_text=_("The name/title of the resource. Avoid using backslashes in the name."))
    long_title_raw = models.CharField(_('long title'), max_length=200, blank=True, null=True,
        help_text=_("This is the long title of the resource."))
    uri_path = models.CharField(_('resource path'), max_length=500, db_index=True,
        help_text=_("Path used in URI to find this resource."))
    description = models.CharField(_('description'), blank=True, max_length=250,
        help_text=_("Optional; description of content."))
    summary = models.TextField(_('summary'), blank=True,
        help_text=_('Summary of resource content.'))
    # Menus
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.PROTECT)
    order = models.PositiveIntegerField(_('Order'), default=100,
        help_text=_('Ordering used to render element.'))
    menu_title_raw = models.CharField(_('menu title'), max_length=100, blank=True,
        help_text=_("Optional name of page to display in menu entries. If not supplied the title field is used."))
    menu_class = models.CharField(_('menu CSS class'), max_length=50, blank=True,
        help_text=_("Value to set template variable menuClass, to apply to menu items."))
    hide_from_menu = models.BooleanField(_('hide from menu'), default=False,
        help_text=_("Do not display this page in generated menus."))
    # Options
    cacheable = models.BooleanField(_('cacheable'), default=True,
        help_text=_("Is the generated content cacheable."))
    published = models.BooleanField(_('published'), default=False,
        help_text=_("The resource is published."))
    publish_date = models.DateTimeField(_('go live date'), null=True, blank=True,
        help_text=_("Optional; if date is set this resource will go live once this date is reached."))
    unpublish_date = models.DateTimeField(_('expiry date'), null=True, blank=True,
        help_text=_("Optional; if date is set this resource will expire once this date has passed."))
    deleted = models.BooleanField(_('deleted'), default=False,
        help_text=_("The resource should be treated as deleted and not displayed to the public at any time."))
    # Content
    resource_type = models.CharField(_('resource type'), max_length=10, choices=RESOURCE_TYPES, default='content')
    content = models.TextField(_('content'), null=True, blank=True)
    # Content options
    template = models.ForeignKey(Template, blank=True, null=True,
        help_text=_("Template to use when rendering content."))
    mime_type = models.CharField(_('MIME type'), choices=MIME_TYPES, default='text/html', max_length=25,
        help_text=_("Mime-type to be set for this resource."))
    content_disposition = models.CharField(_('content disposition'), choices=CONTENT_DISPOSITIONS, blank=True, max_length=15,
        help_text=_("Optional; disposition of content."))
    # Tracking
    created_by = models.ForeignKey(User, related_name='cms_resources')
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True)

    objects = ResourceManager()

    class Meta:
        verbose_name = _('resource')
        verbose_name_plural = _('resources')
        permissions = (('preview_resource', 'Can preview resource'), )
        ordering = ['order', 'title', ]
        unique_together = (('uri_path', 'published', ), )

    def __unicode__(self):
        return '%s [%s]' % (
            self.title, Resource.STATUS_EXPANDED[self.published_status][1])

    @models.permalink
    def get_absolute_url(self):
        return 'warthog-preview', [str(self.pk)]

    def clean(self):
        # Ensure dates are valid
        if (self.publish_date is not None) and \
           (self.unpublish_date is not None) and \
           (self.publish_date > self.unpublish_date):
            raise ValidationError('Publish date must be prior to the Un-publish date.')

    @property
    def published_status(self):
        """
        Determine publish status of this resource.
        """
        if self.deleted:
            return self.STATUS_DELETED
        if self.published:
            now = timezone.now()
            if (self.publish_date is not None) and now < self.publish_date:
                return self.STATUS_SCHEDULED
            elif (self.unpublish_date is not None) and now > self.unpublish_date:
                return self.STATUS_EXPIRED
            else:
                return self.STATUS_LIVE
        return self.STATUS_UNPUBLISHED

    @property
    def is_live(self):
        """
        Is this model considered live.
        """
        return self.published_status == self.STATUS_LIVE

    @property
    def is_root(self):
        """
        Is this model at the root.
        """
        return not bool(self.parent)

    @property
    def is_link(self):
        """
        Is this model a link type.
        """
        return self.resource_type == 'link'

    @property
    def menu_title(self):
        """
        Title to appear in any menus (uses title if menu_title_raw is bool(False)).
        """
        return self.menu_title_raw or self.title

    @property
    def long_title(self):
        """
        Long title (uses title if long_title_raw is bool(False)).
        """
        return self.long_title_raw or self.title

    def html_status(self):
        """
        HTML representation of the status (primarily for use in Admin).
        """
        code, name, help_text = Resource.STATUS_EXPANDED[self.published_status]
        return '<span class="warthog-status-%s" title="%s">%s</span>' % (
            code, unicode(help_text), unicode(name))
    html_status.short_description = _('status')
    html_status.allow_tags = True
