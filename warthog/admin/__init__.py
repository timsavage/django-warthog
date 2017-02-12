# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.utils import ErrorList
from django.contrib.admin import helpers
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from urlparse import unquote

from .forms import ResourceFieldsForm, ResourceAddForm
from .. import cache
from ..models import Template, ResourceType, ResourceTypeField, Resource


class CachedModelAdmin(admin.ModelAdmin):
    """Model admin class with built in cache clear actions"""
    actions = 'clear_cache'

    def clear_cache(self, request, queryset):
        map(cache.clear_model, queryset)
        count = len(queryset)
        if count > 1:
            message = '%s objects where' % count
        else:
            message = '1 object was'
        self.message_user(request, "%s invalidated from cache." % message)
    clear_cache.short_description = 'Invalidate selected objects in cache'


class TemplateAdmin(admin.ModelAdmin):
    """
    Admin class for Template model.
    """
    fieldsets = [
        (None, {
            'fields': ('site', 'name', 'description', 'cacheable', ) ,
        }),
        ('Content', {
            'fields': ('mime_type', 'content', ),
            'classes': ('wide', 'monospace', ),
        }),
        ('Details', {
            'fields': ('created', 'updated', ),
        }),
    ]
    list_display = ('name', 'description', 'created', 'updated', )
    list_display_links = ('name', )
    readonly_fields = ('created', 'updated', )
    save_on_top = True
    save_as = True

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = super(TemplateAdmin, self).get_queryset(request)
        if request.user.is_superuser and 'all' in request.GET:
            return qs
        return qs.filter(site=settings.SITE_ID)

admin.site.register(Template, TemplateAdmin)


class ResourceTypeFieldInline(admin.TabularInline):
    model = ResourceTypeField
    extra = 1


class ResourceTypeAdmin(admin.ModelAdmin):
    inlines = (ResourceTypeFieldInline, )
    list_display = ('name', 'description', 'child_types_list', 'created', 'updated', )
    list_display_superuser = ('name', 'site_summary', 'description', 'child_types_list', 'created', 'updated', )
    prepopulated_fields = {'code': ('name', )}
    save_on_top = True
    save_as = True
    filter_horizontal = ('child_types',)

    def site_summary(self, obj):
        """Summary of sites."""
        return ', '.join(s.name for s in obj.site.all())
    site_summary.short_description = _('Sites')

    def child_types_list(self, obj):
        return ', '.join(str(c.name) for c in obj.child_types.all())
    child_types_list.short_description = _('child types')

    def get_list_display(self, request):
        if request.user.is_superuser:
            return self.list_display_superuser
        else:
            return self.list_display

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = super(ResourceTypeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(site=settings.SITE_ID)

admin.site.register(ResourceType, ResourceTypeAdmin)


class ResourceErrorList(ErrorList):
    """
    Stores all errors for the form/formsets in an add/change stage view.
    """
    def __init__(self, form, fields_form):
        super(ResourceErrorList, self).__init__()
        if form.is_bound:
            self.extend(form.errors.values())
        if fields_form.is_bound:
            self.extend(fields_form.errors.values())


class ResourceAdmin(CachedModelAdmin):
    """
    Admin class for Resource model.
    """
    fieldsets = [
        (None, {
            'fields': ('title', 'slug', 'uri_path', ('published', 'hide_from_menu'),
                       ('publish_date', 'unpublish_date'),),
        }),
        ('Details', {
            'fields': (('created', 'updated'),),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('site', 'parent', 'menu_title_raw', 'menu_class', 'order', 'edit_lock', ),
        }),
    ]
    add_fieldsets = [
        (None, {
            'fields': ('site', 'type', 'title', 'slug', 'parent', )
        }),
        ('Hidden', {
            'classes': ('hidden',),
            'fields': ('order', )
        }),
    ]
    list_display = ('html_status', 'title', 'order', 'resource_path', 'html_type', 'published', 'publish_summary',
                    'unpublish_summary', 'html_actions', )
    list_display_superuser = ('html_status', 'site', 'order', 'title', 'resource_path', 'html_type', 'published',
                              'publish_summary', 'unpublish_summary', 'html_actions', )
    list_editable = ('order', )
    list_display_links = ('title', )
    list_filter = ('published', 'deleted', 'type', )
    actions = ('make_published', 'make_unpublished', 'clear_cache',)
    prepopulated_fields = {'slug': ('title', )}
    readonly_fields = ('created', 'updated', 'uri_path', 'edit_lock', 'site',)
    readonly_fields_superuser = ('created', 'updated', )
    save_on_top = True
    save_as = False

    def html_status(self, obj):
        """HTML representation of the status (primarily for use in Admin)."""
        code, name, help_text = Resource.STATUS_EXPANDED[obj.published_status]
        return '<span class="warthog-status warthog-status-%s" title="%s">%s</span>' % (
            code, unicode(help_text), unicode(name) + (', hidden' if obj.hide_from_menu else ''))
    html_status.short_description = _('status')
    html_status.allow_tags = True

    def resource_path(self, obj):
        """ Path to resource """
        return '<a href="%s">%s</a>' % (obj.get_absolute_url(), obj.uri_path)
    resource_path.short_description = _('Resource Path')
    resource_path.allow_tags = True

    def html_actions(self, obj):
        """Actions within the list"""
        child_types = obj.type.child_types.all()
        add_uri = reverse('admin:warthog_resource_add')
        actions = []
        for type in child_types:
            actions.append('<li><a href="%s?parent=%s&type=%s">Add %s resource</a></li>' % (
                add_uri, obj.pk, type.pk, type.name))
        return '<ul>%s</ul>' % ''.join(actions)
    html_actions.short_description = _('Actions')
    html_actions.allow_tags = True

    def html_type(self, obj):
        """HTML representation of the status (primarily for use in Admin)."""
        return '<span title="%s">%s</span>' % (obj.type.description, obj.type)
    html_type.short_description = _('type')
    html_type.allow_tags = True

    def publish_summary(self, obj):
        """Summary of publish dates."""
        if obj.publish_date:
            return str(obj.publish_date)
        else:
            return _('immediately')
    publish_summary.short_description = _('go live')

    def unpublish_summary(self, obj):
        """Summary of un-publish dates."""
        if obj.unpublish_date:
            return str(obj.unpublish_date)
        else:
            return _('never')
    unpublish_summary.short_description = _('expire ')

    def make_published(self, request, queryset):
        rows_updated = queryset.update(published=True)
        if rows_updated == 1:
            message_bit = "1 resource was"
        else:
            message_bit = "%s resources were" % rows_updated
        self.message_user(request, "%s successfully published." % message_bit)
    make_published.short_description = _('Publish selected resources')

    def make_unpublished(self, request, queryset):
        rows_updated = queryset.update(published=False)
        if rows_updated == 1:
            message_bit = "1 resource was"
        else:
            message_bit = "%s resources were" % rows_updated
        self.message_user(request, "%s successfully un-published." % message_bit)
    make_unpublished.short_description = _('Un-publish selected resources')

    def save_model(self, request, obj, form, change):
        import posixpath
        if not obj.uri_path:
            if obj.parent:
                obj.uri_path = posixpath.join(obj.parent.uri_path, obj.slug)
            else:
                obj.uri_path = '/'
        obj.save()

    def get_list_display(self, request):
        if request.user.is_superuser and 'all' in request.GET:
            return self.list_display_superuser
        else:
            return self.list_display

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('warthog.admin_resource'):
            return self.readonly_fields_superuser
        else:
            return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(ResourceAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            return ResourceAddForm
        return super(ResourceAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = super(ResourceAdmin, self).get_queryset(request)
        if request.user.is_superuser and 'all' in request.GET:
            return qs
        return qs.filter(site=settings.SITE_ID)

    def response_add(self, request, obj, post_url_continue=None):
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(ResourceAdmin, self).response_add(request, obj, post_url_continue)

    def save_fields_form(self, request, form, obj, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        return form.save_to(obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_locked_for_user(request.user):
            return False
        return super(ResourceAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_locked_for_user(request.user):
            return False
        return super(ResourceAdmin, self).has_delete_permission(request, obj)

    @transaction.atomic
    def change_view(self, request, object_id, form_url='', extra_context=None):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

#        if request.method == 'POST' and "_saveasnew" in request.POST:
#            return self.add_view(request, form_url=reverse('admin:%s_%s_create' %
#                                                           (opts.app_label, opts.module_name),
#                current_app=self.admin_site.name), resource_type_code=obj.type)

        ModelForm = self.get_form(request, obj)
        initial=dict(obj.fields.all().values_list('code', 'value'))
        if request.method == 'POST':
            form = ModelForm(data=request.POST, instance=obj)
            fields_form = ResourceFieldsForm(obj.type, instance=obj, initial=initial, prefix='fields', data=request.POST, files=request.FILES)

            if form.is_valid() and fields_form.is_valid():
                obj = self.save_form(request, form, change=False)
                self.save_model(request, obj, form, False)
                self.save_fields_form(request, fields_form, obj, False)
                self.log_addition(request, obj)
                return self.response_change(request, obj)
        else:
            form = ModelForm(instance=obj)

            # Populate form
            fields_form = ResourceFieldsForm(obj.type, instance=obj, initial=initial, prefix='fields')

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request, obj)),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media + fields_form.media

        context = {
            'title': _('Change %s %s') % (force_unicode(obj.type.name), force_unicode(opts.verbose_name)),
            'adminform': adminForm,
            'fields_adminform': fields_form,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': True,
            'media': media,
            'inline_admin_formsets': [],
            'errors': ResourceErrorList(form, fields_form),
            'app_label': opts.app_label,
        }
        return self.render_change_form(request, context, change=True, obj=obj, form_url=form_url)

admin.site.register(Resource, ResourceAdmin)
