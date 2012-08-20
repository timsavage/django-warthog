from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from warthog.managers import CachingManager, ResourceManager, ResourceTypeManager
from warthog import fields


code_name = RegexValidator(r'^\w+$', message='Code value')


class Template(models.Model):
    """Defines a template.

    A template is used as the scaffolding for a page (or section of a page).

    Variables can be used within a template to define additional data items
    to be used when rendering the page.

    """
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

    # Description
    name = models.CharField(_('name'), max_length=100, db_index=True, unique=True)
    description = models.CharField(_('description'), max_length=250, blank=True,
        help_text=_("Optional description of template."))
    # Content
    content = models.TextField(_('content'))
    mime_type = models.CharField(_('MIME type'), choices=MIME_TYPES, default='text/html',
        max_length=25, help_text=_("Mime-type to be set for this template."))
    # Options
    cacheable = models.BooleanField(_('cachable'), default=True)
    # Tracking
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ['name', ]

    def __unicode__(self):
        return self.name


class ResourceType(models.Model):
    """
    Defines a resource and what fields that are associated with it.
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    code = models.CharField(_('code'), max_length=50, unique=True, validators=[code_name],
        help_text=_('Code name used to reference this field.'))
    description = models.CharField(_('description'), max_length=500, blank=True,
        help_text=_('Optional description of this resource type.'))
    default_template = models.CharField(_('default template'), max_length=500,
        help_text=_('Name of the default template used to render resources of this type.'))
    child_types = models.ManyToManyField('self', verbose_name=_('Child types'), symmetrical=False, blank=True,
        help_text=_('Resource types that can be created as leaf nodes of the current resource.'))
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True)

    objects = ResourceTypeManager()

    class Meta:
        verbose_name = _('resource type')
        verbose_name_plural = _('resource types')

    def __unicode__(self):
        return self.name


class ResourceTypeField(models.Model):
    """
    Defines a field that is part of a resource.
    """
    resource_type = models.ForeignKey(ResourceType, related_name='fields')
    code = models.CharField(_('code'), max_length=50, validators=[code_name],
        help_text=_('Code name used to reference this field.'))
    field_type = models.CharField(_('field type'), max_length=25,
        choices=fields.get_field_choices())
    required = models.BooleanField(_('required'), default=False,
        help_text=_('This field is required'))
    label_raw = models.CharField(_('label'), max_length=200, null=True, blank=True,
        help_text=_('Label displayed to user.'))
    help_text = models.CharField(_('help text'), max_length=500, null=True, blank=True,
        help_text=_('Optional help message for describing the use of the field.'))

    objects = CachingManager()

    class Meta:
        verbose_name = _('resource type field')
        verbose_name_plural = _('resource type fields')
        unique_together = (('resource_type', 'code'), )

    def __unicode__(self):
        return self.code

    @property
    def label(self):
        return self.label_raw if self.label_raw else self.code

    def get_kwargs(self):
        return {
            'label': self.label,
            'required': self.required,
            'help_text': self.help_text,
        }


class Resource(models.Model):
    """
    CMS Resource model, resource that is served on a particular URI.
    """

    CONTENT_DISPOSITIONS = (
        ('',           _('None')),
        ('inline',     _('Inline')),
        ('attachment', _('Attachment'))
    )

    # Statuses of a resource
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

    type = models.ForeignKey(ResourceType, related_name=_('resources'))
    title = models.CharField(_('title'), max_length=100,
        help_text=_("The name/title of the resource. Avoid using backslashes in the name."))
    slug = models.CharField(_('slug'), max_length=100, null=True,
        help_text=_('Resource identifier used to create URI path.'))
    uri_path = models.CharField(_('resource path'), max_length=500, db_index=True, unique=True,
        help_text=_("Path used in URI to find this resource."), blank=True)
    published = models.BooleanField(_('published'), default=False,
        help_text=_("The resource is published."))
    publish_date = models.DateTimeField(_('go live date'), null=True, blank=True,
        help_text=_("Optional; if date is set this resource will go live once this date is reached."))
    unpublish_date = models.DateTimeField(_('expiry date'), null=True, blank=True,
        help_text=_("Optional; if date is set this resource will expire once this date has passed."))
    # Menu
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    menu_title_raw = models.CharField(_('menu title'), max_length=100, blank=True,
        help_text=_("Optional name of page to display in menu entries. If not supplied the title field is used."))
    menu_class = models.CharField(_('menu CSS class'), max_length=50, blank=True,
        help_text=_("Value to set template variable menuClass, to apply to menu items."))
    hide_from_menu = models.BooleanField(_('hide from navigation'), default=False,
        help_text=_("Do not display this page in generated menus."))
    # Flags
    order = models.PositiveIntegerField(_('Order'), default=100,
        help_text=_('Ordering used to render element.'))
    deleted = models.BooleanField(_('deleted'), default=False,
        help_text=_("The resource should be treated as deleted and not displayed to the public at any time."))
    # Details
    created = models.DateTimeField(_('creation date'), auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True)

    objects = ResourceManager()

    class Meta:
        verbose_name = _('resource')
        verbose_name_plural = _('resources')
        permissions = (('preview_resource', 'Can preview resource'), )
        ordering = ['order', 'uri_path', 'title', ]
        unique_together = (('slug', 'parent', ), )

    def __unicode__(self):
        return '[%s] - %s (%s)' % (
            self.title, Resource.STATUS_EXPANDED[self.published_status][1], self.uri_path)

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
    def children(self):
        return self.resource_set.filter(deleted=False, published=True)

    @property
    def published_status(self):
        """Determine publish status of this resource."""
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
        """Is this model considered live."""
        return self.published_status == self.STATUS_LIVE

    @property
    def is_root(self):
        """Is this model at the root."""
        return not bool(self.parent)

    @property
    def menu_title(self):
        """Title to appear in any menus (uses title if menu_title_raw is
        bool(False))."""
        return self.menu_title_raw or self.title


class ResourceField(models.Model):
    """Template variable that is applied to a resource."""
    resource = models.ForeignKey(Resource, related_name='fields')
    code = models.CharField(_('code'), max_length=50, validators=[code_name],
        help_text=_('Code name used to reference this field.'))
    value = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('resource', 'code',), )

    def __unicode__(self):
        return "%s=%s " % (self.code, self.value)
