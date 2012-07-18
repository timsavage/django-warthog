from django.contrib import admin
from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from warthog import cache
from warthog.models import Template, TemplateVariable, ContentBlock, Resource, ResourceTemplateVariable


# Try to load TINY MCE
HtmlWidget = forms.Textarea
#if settings.CMS_USE_TINYMCE:
#    try:
#        #noinspection PyUnresolvedReferences
#        from tinymce.widgets import AdminTinyMCE
#        HtmlWidget = AdminTinyMCE
#    except ImportError:
#        pass


class CachedModelAdmin(admin.ModelAdmin):
    """Model admin class with built in cache clear actions"""
    actions = 'clear_cache'

    def clear_cache(self, request, queryset):
        map(cache.clear_model, queryset)
        count = len(queryset)
        if count > 1:
            message = '%s objects where'
        else:
            message = '1 object was'
        self.message_user(request, "%s invalidated from cache." % message)
    clear_cache.short_description = 'Invalidate selected objects in cache'


class TemplateVariableInline(admin.TabularInline):
    model = TemplateVariable
    extra = 1


class TemplateAdminForm(ModelForm):
    class Meta:
        model = Template
        widgets = {
            'content': HtmlWidget(attrs={'cols': 80, 'rows': 30}),
            }


class TemplateAdmin(admin.ModelAdmin):
    """
    Admin class for Template model.
    """
    form = TemplateAdminForm
    fieldsets = [
        (None, {
            'fields': ('name', 'description', 'cacheable', ) ,
            }),
        ('Content', {
            'fields': ('content', ),
            'classes': ('wide', 'monospace', ),
            }),
        ('Details', {
            'fields': ('created', 'updated', ),
            }),
        ]
    list_display = ('name', 'description', 'created', 'updated', )
    list_display_links = ('name', )
    readonly_fields = ('created', 'updated', )
    inlines = [TemplateVariableInline]
    save_on_top = True
    save_as = True
admin.site.register(Template, TemplateAdmin)


class ContentBlockAdminForm(ModelForm):
    class Meta:
        model = ContentBlock
        widgets = {
            'content': HtmlWidget(attrs={'cols': 80, 'rows': 30}),
            }


class ContentBlockAdmin(admin.ModelAdmin):
    """
    Admin class for Content model.
    """
    form = ContentBlockAdminForm
    fieldsets = [
        (None, {
            'fields': ('name', 'description', 'cacheable', ),
            }),
        ('Content', {
            'fields': ('content', ),
            'classes': ('wide', ),
            }),
        ('Details', {
            'fields': ('created', 'updated', ),
            }),
    ]
    list_display = ('name', 'description', 'created', 'updated', )
    list_display_links = ('name', )
    readonly_fields = ('created', 'updated', )
admin.site.register(ContentBlock, ContentBlockAdmin)


class ResourceTemplateVariableInline(admin.TabularInline):
    model = ResourceTemplateVariable
    extra = 1


class ResourceAdminForm(ModelForm):
    class Meta:
        model = Resource
        widgets = {
            'content': HtmlWidget(attrs={'cols': 80, 'rows': 30}),
            }


class ResourceAdmin(CachedModelAdmin):
    """
    Admin class for Resource model.
    """
    form = ResourceAdminForm
    fieldsets = [
        (None, {
            'fields': ('title', 'long_title_raw', 'uri_path', 'description', 'published', ('publish_date', 'unpublish_date'), ),
            }),
        ('Content', {
            'fields': ('resource_type', 'template', 'summary', 'content', ),
            'classes': ('wide', ),
            }),
        ('Menu', {
            'fields': ('parent', 'menu_title_raw', 'menu_class', 'hide_from_menu', ),
            }),
        ('Advanced', {
            'fields': ( 'mime_type', 'content_disposition', 'cacheable', ),
            }),
        ('Details', {
            'fields': ('created_by', 'created', 'updated',),
            }),
    ]
    list_display = ('html_status', 'title', 'uri_path', 'html_type', 'published', 'publish_summary', 'unpublish_summary', )
    list_display_links = ('title', 'uri_path', )
    list_filter = ('published', 'deleted', )
    actions = ('make_published', 'make_unpublished', )
    prepopulated_fields = {'uri_path': ('title', )}
    readonly_fields = ('created_by', 'created', 'updated', )
    save_on_top = True
    save_as = True
    inlines = [ResourceTemplateVariableInline]

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
            obj.resource_type, obj.get_resource_type_display())
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
        if not obj.created_by_id:
            obj.created_by_id = request.user.id
        if not obj.uri_path.startswith('/'):
            obj.uri_path = '/' + obj.uri_path
        obj.save()
admin.site.register(Resource, ResourceAdmin)
