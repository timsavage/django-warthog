from django.contrib import admin
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.util import ErrorList
from django.contrib.admin import helpers
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from warthog import cache
from warthog.models import Template, ResourceType, ResourceTypeField, Resource
from warthog.admin.forms import ResourceFieldsForm, ResourceAddForm


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
    list_display = ('name', 'description', 'child_types_list', 'created', 'updated', )
    prepopulated_fields = {'code': ('name', )}
    save_on_top = True
    save_as = True
    filter_horizontal = ('child_types',)

    def child_types_list(self, obj):
        return ', '.join([str(c.name) for c in obj.child_types.all()])
    child_types_list.short_description = _('child types')


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
            'fields': ('title', 'slug', 'uri_path', ('published', 'hide_from_menu') , ('publish_date', 'unpublish_date'), ),
        }),
        ('Details', {
            'fields': (('created', 'updated'),),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('parent', 'menu_title_raw', 'menu_class', 'order', ),
        }),
    ]
    add_fieldsets = [
        (None, {
            'fields': ('type', 'title', 'slug', 'parent', )
        }),
        ('Hidden', {
            'classes': ('hidden',),
            'fields': ('order', )
        }),
    ]
    list_display = ('html_status', 'title', 'uri_path', 'html_type', 'published', 'publish_summary', 'unpublish_summary', 'html_actions', )
    list_display_links = ('title', 'uri_path', )
    list_filter = ('published', 'deleted', 'type', )
    actions = ('make_published', 'make_unpublished', 'clear_cache', )
    prepopulated_fields = {'slug': ('title', )}
    readonly_fields = ('created', 'updated', 'uri_path', )
    readonly_fields_superuser = ('created', 'updated', )
    save_on_top = True
    save_as = True

    def html_status(self, obj):
        """HTML representation of the status (primarily for use in Admin)."""
        code, name, help_text = Resource.STATUS_EXPANDED[obj.published_status]
        return '<span class="warthog-status warthog-status-%s" title="%s">%s</span>' % (
            code, unicode(help_text), unicode(name) + (', hidden' if obj.hide_from_menu else ''))
    html_status.short_description = _('status')
    html_status.allow_tags = True

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
            obj.uri_path = posixpath.join(obj.parent.uri_path, obj.slug)
        obj.save()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
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

    def response_add(self, request, obj, post_url_continue='../%s/'):
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(ResourceAdmin, self).response_add(request, obj, post_url_continue)

    def save_fields_form(self, request, form, obj, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        return form.save_to(obj)

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

#        if request.method == 'POST' and "_saveasnew" in request.POST:
#            return self.add_view(request, form_url=reverse('admin:%s_%s_create' %
#                                                           (opts.app_label, opts.module_name),
#                current_app=self.admin_site.name), resource_type_code=obj.type)

        ModelForm = self.get_form(request, obj)
        if request.method == 'POST':
            form = ModelForm(data=request.POST, instance=obj)
            fields_form = ResourceFieldsForm(obj.type, prefix='fields', data=request.POST, files=request.FILES)

            if form.is_valid() and fields_form.is_valid():
                obj = self.save_form(request, form, change=False)
                self.save_model(request, obj, form, False)
                self.save_fields_form(request, fields_form, obj, False)
                self.log_addition(request, obj)
                return self.response_change(request, obj)
        else:
            form = ModelForm(instance=obj)

            # Populate form
            fields_form = ResourceFieldsForm(obj.type, initial=dict(obj.fields.all().values_list('code', 'value')), prefix='fields')

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
