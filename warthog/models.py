# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as t
from . import resource_types
from .managers import CachingManager, ResourceManager, ResourceTypeManager


code_name = RegexValidator(r'^[-\w]+$', message='Code value')


class Template(models.Model):
    """Defines a template.

    A template is used as the scaffolding for a page (or section of a page).

    Variables can be used within a template to define additional data items
    to be used when rendering the page.

    """
    MIME_TYPES = (
        ('Text (text/*)', (
            ('text/html',          t('HTML')),
            ('text/plain',         t('Text')),
            ('text/css',           t('CSS')),
            ('text/javascript',    t('JavaScript')),
            ('text/csv',           t('CSV')),
            ('text/xml',           t('XML')),
            ('text/cachemanifest', t('HTML5 Cache Manifest')),
        )),
        ('Application (application/*)', (
            ('application/xhtml+xml',  t('XHTML')),
            ('application/javascript', t('JavaScript')),
            ('application/json',       t('JSON')),
        ))
    )

    # Description
    site = models.ManyToManyField(Site, default=[settings.SITE_ID])
    name = models.CharField(t('name'), max_length=100, db_index=True, unique=True)
    description = models.CharField(t('description'), max_length=250, blank=True,
        help_text=t("Optional description of template."))
    # Content
    content = models.TextField(t('content'))
    mime_type = models.CharField(t('MIME type'), choices=MIME_TYPES, default='text/html',
        max_length=25, help_text=t("Mime-type to be set for this template."))
    # Options
    cacheable = models.BooleanField(t('cachable'), default=True)
    # Tracking
    created = models.DateTimeField(t('creation date'), auto_now_add=True)
    updated = models.DateTimeField(t('last modified'), auto_now=True)

    class Meta:
        verbose_name = t('template')
        verbose_name_plural = t('templates')
        ordering = ['name', ]

    def __unicode__(self):
        return self.name


class ResourceType(models.Model):
    """
    Defines a resource and what fields that are associated with it.
    """
    site = models.ManyToManyField(Site, default=[settings.SITE_ID])
    name = models.CharField(
        verbose_name=t('name'),
        max_length=50, unique=True
    )
    code = models.CharField(
        verbose_name=t('code'),
        max_length=50, unique=True, validators=[code_name],
        help_text=t('Code name used to reference this field.')
    )
    description = models.CharField(
        verbose_name=t('description'),
        max_length=500, blank=True,
        help_text=t('Optional description of this resource type.')
    )
    default_template = models.CharField(
        verbose_name=t('default template'),
        max_length=500,
        help_text=t('Name of the default template used to render resources of this type.')
    )
    child_types = models.ManyToManyField(
        to='self',
        verbose_name=t('Child types'),
        symmetrical=False, blank=True,
        help_text=t('Resource types that can be created as leaf nodes of the current resource.')
    )
    created = models.DateTimeField(
        verbose_name=t('creation date'),
        auto_now_add=True
    )
    updated = models.DateTimeField(
        verbose_name=t('last modified'),
        auto_now=True
    )

    objects = ResourceTypeManager()

    class Meta:
        verbose_name = t('resource type')
        verbose_name_plural = t('resource types')

    def __unicode__(self):
        return self.name


class ResourceTypeField(models.Model):
    """
    Defines a field that is part of a resource.
    """
    resource_type = models.ForeignKey(ResourceType, related_name='fields')
    code = models.CharField(
        verbose_name=t('code'),
        max_length=50, validators=[code_name],
        help_text=t('Code name used to reference this field.')
    )
    field_type = models.CharField(
        verbose_name=t('field type'),
        max_length=25,
        choices=resource_types.library.choices
    )
    required = models.BooleanField(
        verbose_name=t('required'),
        default=False,
        help_text=t('This field is required')
    )
    label_raw = models.CharField(
        verbose_name=t('label'),
        max_length=200, null=True, blank=True,
        help_text=t('Label displayed to user.')
    )
    help_text = models.CharField(
        verbose_name=t('help text'),
        max_length=500, null=True, blank=True,
        help_text=t('Optional help message for describing the use of the field.')
    )

    objects = CachingManager()

    class Meta:
        verbose_name = t('resource type field')
        verbose_name_plural = t('resource type fields')
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

    def create_form_field(self):
        """
        Create an instance of a form field that that is represented by this model.
        """
        return resource_types.library[self.field_type].create_form_field(self.get_kwargs())


class Resource(models.Model):
    """
    CMS Resource model, resource that is served on a particular URI.
    """

    CONTENT_DISPOSITIONS = (
        ('',           t('None')),
        ('inline',     t('Inline')),
        ('attachment', t('Attachment'))
    )

    # Statuses of a resource
    STATUS_DELETED = 0
    STATUS_UNPUBLISHED = 1
    STATUS_EXPIRED = 2
    STATUS_SCHEDULED = 3
    STATUS_LIVE = 4

    STATUS_EXPANDED = {
        STATUS_DELETED: ('deleted', t('Deleted'), t('This resources has been deleted.')),
        STATUS_UNPUBLISHED: ('unpublished', t('Unpublished'), t('This resource has not been published.')),
        STATUS_EXPIRED: ('expired', t('Expired'), t('This resource has expired (un-publish date is in the past).')),
        STATUS_SCHEDULED: ('scheduled', t('Scheduled'), t('This resource is scheduled to be published (publish date is in the future).')),
        STATUS_LIVE: ('live', t('Live'), t('This resource is live.')),
    }

    site = models.ForeignKey(Site, default=settings.SITE_ID)
    type = models.ForeignKey(ResourceType, related_name=t('resources'))
    title = models.CharField(
        verbose_name=t('title'),
        max_length=100,
        help_text=t("The name/title of the resource. Avoid using backslashes in the name.")
    )
    slug = models.CharField(
        verbose_name=t('slug'),
        max_length=100,
        null=True,
        help_text=t('Resource identifier used to create URI path.')
    )
    uri_path = models.CharField(
        verbose_name=t('resource path'),
        max_length=500, db_index=True,
        blank=True,
        help_text=t("Path used in URI to find this resource.")
    )
    published = models.BooleanField(
        verbose_name=t('published'),
        default=False,
        help_text=t("The resource is published.")
    )
    publish_date = models.DateTimeField(
        verbose_name=t('go live date'),
        null=True, blank=True,
        help_text=t("Optional; if date is set this resource will go live once this date is reached.")
    )
    unpublish_date = models.DateTimeField(
        verbose_name=t('expiry date'),
        null=True, blank=True,
        help_text=t("Optional; if date is set this resource will expire once this date has passed.")
    )
    # Menu
    parent = models.ForeignKey(
        to='self',
        null=True, blank=True,
        on_delete=models.PROTECT
    )
    menu_title_raw = models.CharField(
        verbose_name=t('menu title'),
        max_length=100, blank=True,
        help_text=t("Optional name of page to display in menu entries. If not supplied the title field is used.")
    )
    menu_class = models.CharField(
        verbose_name=t('menu CSS class'),
        max_length=50, blank=True,
        help_text=t("Value to set template variable menuClass, to apply to menu items.")
    )
    hide_from_menu = models.BooleanField(
        verbose_name=t('hide from navigation'),
        default=False,
        help_text=t("Do not display this page in generated menus.")
    )
    # Flags
    order = models.PositiveIntegerField(
        verbose_name=t('Order'),
        default=100,
        help_text=t('Ordering used to render element.')
    )
    deleted = models.BooleanField(
        verbose_name=t('deleted'),
        default=False,
        help_text=t("The resource should be treated as deleted and not displayed to the public at any time.")
    )
    edit_lock = models.BooleanField(
        verbose_name=t('Edit locked'),
        default=False,
        help_text=t(
            "Lock this resource so only `Can admin resources` permission can edit"
            "this resource. This flag is used to prevent structural resources from being modified."
        )
    )

    # Details
    created = models.DateTimeField(t('creation date'), auto_now_add=True)
    updated = models.DateTimeField(t('last modified'), auto_now=True)

    objects = ResourceManager()

    class Meta:
        verbose_name = t('resource')
        verbose_name_plural = t('resources')
        permissions = (
            ('preview_resource', 'Can preview resource'),
            ('admin_resource', 'Can admin resources.'),
        )
        ordering = ['order', 'uri_path', 'title', ]
        unique_together = (('site', 'slug', 'parent', ), )

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
        return self.resource_set.filter_front()

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

    def is_locked_for_user(self, user):
        """Check if a particular user can edit this resource"""
        if self.edit_lock:
            return not user.has_perm('warthog.admin_resource')
        return False

    def can_serve(self, user, allow_superuser=True, permission='preview_resource'):
        """Determine if this resource can be served.

        :param user: User we are checking against.
        :param allow_superuser: Allow superusers to view this resource.
        :param permission: Permission required to view this resource.

        """
        if self.is_live:
            return True

        if allow_superuser and user.is_superuser:
            return True

        if permission and user.has_perm(permission):
            return True

        return False


class ResourceField(models.Model):
    """Template variable that is applied to a resource."""
    resource = models.ForeignKey(Resource, related_name='fields')
    code = models.CharField(
        verbose_name=t('code'),
        max_length=50, validators=[code_name],
        help_text=t('Code name used to reference this field.')
    )
    value = models.TextField(
        blank=True, null=True
    )

    class Meta:
        unique_together = (('resource', 'code',), )

    def __unicode__(self):
        return "%s=%s" % (self.code, self.value)
