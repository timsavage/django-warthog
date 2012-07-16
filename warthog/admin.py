from django.contrib import admin
from django import forms
from django.forms.models import ModelForm
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


class ResourceAdmin(admin.ModelAdmin):
    """
    Admin class for Resource model.
    """
    form = ResourceAdminForm
    fieldsets = [
        (None, {
            'fields': ('title', 'uri_path', 'parent', 'published', ('publish_date', 'unpublish_date'), ),
            }),
        ('Content', {
            'fields': ('resource_type', 'template', 'summary', 'content', ),
            'classes': ('wide', ),
            }),
        ('Content Extended', {
            'fields': ('long_title_raw', 'description', ),
            }),
        ('Menu', {
            'fields': ('menu_title_raw', 'menu_class', 'hide_from_menu', ),
            }),
        ('Advanced', {
            'fields': ( 'mime_type', 'content_disposition', 'cacheable', ),
            }),
        ('Details', {
            'fields': ('created_by', 'created', 'updated',),
            }),
    ]
    list_display = ('html_status', 'title', 'uri_path', 'published', 'publish_date', 'unpublish_date',  )
    list_display_links = ('title', 'uri_path', )
    list_editable = ('published', )
    list_filter = ('published', 'deleted', )
    prepopulated_fields = {'uri_path': ('title', )}
    readonly_fields = ('created_by', 'created', 'updated', )
    save_on_top = True
    save_as = True
    inlines = [ResourceTemplateVariableInline]

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by_id = request.user.id
        if not obj.uri_path.startswith('/'):
            obj.uri_path = '/' + obj.uri_path
        obj.save()
admin.site.register(Resource, ResourceAdmin)
