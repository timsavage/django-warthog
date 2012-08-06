from django.contrib import admin
from django import forms
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.util import ErrorList
from django.contrib.admin import helpers
from django.http import Http404
from django.shortcuts import render
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from warthog import cache
from warthog.models import Template, ResourceType, ResourceTypeField, Resource, ResourceField
from warthog.forms import ResourceForm, ResourceFieldsForm


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
            'fields': ('name', 'description', 'cacheable', ) ,
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
admin.site.register(Template, TemplateAdmin)


class ResourceTypeFieldInline(admin.TabularInline):
    model = ResourceTypeField
    extra = 1

class ResourceTypeAdmin(admin.ModelAdmin):
    inlines = (ResourceTypeFieldInline, )
    list_display = ('name', 'description', 'created', 'updated', )
    prepopulated_fields = {'code': ('name', )}
    save_on_top = True
    save_as = True

admin.site.register(ResourceType, ResourceTypeAdmin)


class ResourceErrorList(ErrorList):
    """
    Stores all errors for the form/formsets in an add/change stage view.
    """
    def __init__(self, form, fields_form):
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
            'fields': ('title', 'uri_path', 'published', ('publish_date', 'unpublish_date'), ),
        }),
        ('Menu', {
            'fields': ('parent', 'menu_title_raw', 'menu_class', 'hide_from_menu', ),
        }),
        ('Details', {
            'fields': ('created', 'updated',),
        }),
    ]
    list_display = ('html_status', 'title', 'uri_path', 'html_type', 'published', 'publish_summary', 'unpublish_summary', )
    list_display_links = ('title', 'uri_path', )
    list_filter = ('published', 'deleted', )
    actions = ('make_published', 'make_unpublished', 'clear_cache', )
    prepopulated_fields = {'uri_path': ('title', )}
    readonly_fields = ('type', 'created', 'updated', )
    save_on_top = True
    save_as = True

    def html_status(self, obj):
        """HTML representation of the status (primarily for use in Admin)."""
        code, name, help_text = Resource.STATUS_EXPANDED[obj.published_status]
        return '<span class="warthog-status warthog-status-%s" title="%s">%s</span>' % (
            code, unicode(help_text), unicode(name))
    html_status.short_description = _('status')
    html_status.allow_tags = True

    def html_type(self, obj):
        """HTML representation of the status (primarily for use in Admin)."""
        code, name, help_text = Resource.STATUS_EXPANDED[obj.published_status]
        return '<span class="warthog-type warthog-type-%s">%s</span>' % (
            obj.type, obj.get_resource_type_display())
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
        if not obj.uri_path.startswith('/'):
            obj.uri_path = '/' + obj.uri_path
        obj.save()

    def get_urls(self):
        from django.conf.urls import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^$',
                self.admin_site.admin_view(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^add/$',
                self.admin_site.admin_view(self.select_type_view),
                name='%s_%s_add' % info),
            url(r'^add/([-\w]+)/$',
                self.admin_site.admin_view(self.add_view),
                name='%s_%s_create' % info),
            url(r'^(.+)/history/$',
                self.admin_site.admin_view(self.history_view),
                name='%s_%s_history' % info),
            url(r'^(.+)/delete/$',
                self.admin_site.admin_view(self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(.+)/$',
                self.admin_site.admin_view(self.change_view),
                name='%s_%s_change' % info),
        )
        return urlpatterns

    def select_type_view(self, request):
        opts = self.model._meta
        resource_types = ResourceType.objects.all()
        context = {
            'title': _('Select resource type to add'),
            'resource_types': resource_types,
            'app_label': opts.app_label,
            'opts': opts,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, "admin/warthog/resource/select_type.html", context)

    @transaction.commit_on_success
    def add_view(self, request, resource_type_code, form_url=''):
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        resource_type = ResourceType.objects.get(code=resource_type_code)

        ModelForm = self.get_form(request)

        if request.method == 'POST':
            form = ModelForm(data=request.POST)
            fields_form = ResourceFieldsForm(resource_type, prefix='fields', data=request.POST, files=request.FILES)

            if form.is_valid() and fields_form.is_valid():
                resource = self.save_form(request, form, change=False)
                resource.type = resource_type
                self.save_model(request, resource, form, False)

                # Create resource fields
                for code, value in fields_form.cleaned_data.items():
                    resource.fields.create(
                        code=code,
                        value=value,
                    )

                self.log_addition(request, resource)
                return self.response_add(request, resource)
        else:
            form = ModelForm(initial={'type': resource_type.pk})
            fields_form = ResourceFieldsForm(resource_type, prefix='fields')

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media + fields_form.media

        context = {
            'title': _('Add %s %s') % (force_unicode(resource_type.name), force_unicode(opts.verbose_name)),
            'adminform': adminForm,
            'fields_adminform': fields_form,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': [],
            'errors': ResourceErrorList(form, fields_form),
            'app_label': opts.app_label,
            }
        return self.render_change_form(request, context, form_url=form_url, add=True)

    @transaction.commit_on_success
    def change_view(self, request, object_id, form_url='', extra_context=None):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and "_saveasnew" in request.POST:
            return self.add_view(request, form_url=reverse('admin:%s_%s_create' %
                                                           (opts.app_label, opts.module_name),
                current_app=self.admin_site.name), resource_type_code=obj.type)

        ModelForm = self.get_form(request)
        if request.method == 'POST':
            form = ModelForm(data=request.POST, instance=obj)
            fields_form = ResourceFieldsForm(obj.type, prefix='fields', data=request.POST, files=request.FILES)

            if form.is_valid() and fields_form.is_valid():
                resource = self.save_form(request, form, change=False)
                self.save_model(request, resource, form, False)

                # Update resource fields
                resource.fields.all().delete()
                for code, value in fields_form.cleaned_data.items():
                    resource.fields.create(
                        code=code,
                        value=value,
                    )

                self.log_addition(request, resource)
                return self.response_add(request, resource)
        else:
            form = ModelForm(instance=obj)
            fields_form = ResourceFieldsForm(obj.type, initial=dict(obj.fields.all().values_list('code', 'value')), prefix='fields')

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
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
