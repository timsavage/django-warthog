# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='The name/title of the resource. Avoid using backslashes in the name.', max_length=100, verbose_name='title')),
                ('slug', models.CharField(help_text='Resource identifier used to create URI path.', max_length=100, null=True, verbose_name='slug')),
                ('uri_path', models.CharField(help_text='Path used in URI to find this resource.', max_length=500, verbose_name='resource path', db_index=True, blank=True)),
                ('published', models.BooleanField(default=False, help_text='The resource is published.', verbose_name='published')),
                ('publish_date', models.DateTimeField(help_text='Optional; if date is set this resource will go live once this date is reached.', null=True, verbose_name='go live date', blank=True)),
                ('unpublish_date', models.DateTimeField(help_text='Optional; if date is set this resource will expire once this date has passed.', null=True, verbose_name='expiry date', blank=True)),
                ('menu_title_raw', models.CharField(help_text='Optional name of page to display in menu entries. If not supplied the title field is used.', max_length=100, verbose_name='menu title', blank=True)),
                ('menu_class', models.CharField(help_text='Value to set template variable menuClass, to apply to menu items.', max_length=50, verbose_name='menu CSS class', blank=True)),
                ('hide_from_menu', models.BooleanField(default=False, help_text='Do not display this page in generated menus.', verbose_name='hide from navigation')),
                ('order', models.PositiveIntegerField(default=100, help_text='Ordering used to render element.', verbose_name='Order')),
                ('deleted', models.BooleanField(default=False, help_text='The resource should be treated as deleted and not displayed to the public at any time.', verbose_name='deleted')),
                ('edit_lock', models.BooleanField(default=False, help_text='Lock this resource so only `Can admin resources` permission can editthis resource. This flag is used to prevent structural resources from being modified.', verbose_name='Edit locked')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='warthog.Resource', null=True)),
                ('site', models.ForeignKey(default=1, to='sites.Site')),
            ],
            options={
                'ordering': ['order', 'uri_path', 'title'],
                'verbose_name': 'resource',
                'verbose_name_plural': 'resources',
                'permissions': (('preview_resource', 'Can preview resource'), ('admin_resource', 'Can admin resources.')),
            },
        ),
        migrations.CreateModel(
            name='ResourceField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text='Code name used to reference this field.', max_length=50, verbose_name='code', validators=[django.core.validators.RegexValidator(b'^[-\\w]+$', message=b'Code value')])),
                ('value', models.TextField(null=True, blank=True)),
                ('resource', models.ForeignKey(related_name='fields', to='warthog.Resource')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('code', models.CharField(help_text='Code name used to reference this field.', unique=True, max_length=50, verbose_name='code', validators=[django.core.validators.RegexValidator(b'^[-\\w]+$', message=b'Code value')])),
                ('description', models.CharField(help_text='Optional description of this resource type.', max_length=500, verbose_name='description', blank=True)),
                ('default_template', models.CharField(help_text='Name of the default template used to render resources of this type.', max_length=500, verbose_name='default template')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('child_types', models.ManyToManyField(help_text='Resource types that can be created as leaf nodes of the current resource.', to='warthog.ResourceType', verbose_name='Child types', blank=True)),
                ('site', models.ManyToManyField(default=[1], to='sites.Site')),
            ],
            options={
                'verbose_name': 'resource type',
                'verbose_name_plural': 'resource types',
            },
        ),
        migrations.CreateModel(
            name='ResourceTypeField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text='Code name used to reference this field.', max_length=50, verbose_name='code', validators=[django.core.validators.RegexValidator(b'^[-\\w]+$', message=b'Code value')])),
                ('field_type', models.CharField(max_length=25, verbose_name='field type', choices=[(b'char', b'Text'), (b'html', b'HTML'), (b'bool', b'Checkbox'), (b'file', b'File'), (b'time', b'Time'), (b'date', b'Date'), (b'text', b'Text Area'), (b'image', b'Image'), (b'datetime', b'Date Time')])),
                ('required', models.BooleanField(default=False, help_text='This field is required', verbose_name='required')),
                ('label_raw', models.CharField(help_text='Label displayed to user.', max_length=200, null=True, verbose_name='label', blank=True)),
                ('help_text', models.CharField(help_text='Optional help message for describing the use of the field.', max_length=500, null=True, verbose_name='help text', blank=True)),
                ('resource_type', models.ForeignKey(related_name='fields', to='warthog.ResourceType')),
            ],
            options={
                'verbose_name': 'resource type field',
                'verbose_name_plural': 'resource type fields',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='name', db_index=True)),
                ('description', models.CharField(help_text='Optional description of template.', max_length=250, verbose_name='description', blank=True)),
                ('content', models.TextField(verbose_name='content')),
                ('mime_type', models.CharField(default=b'text/html', help_text='Mime-type to be set for this template.', max_length=25, verbose_name='MIME type', choices=[(b'Text (text/*)', ((b'text/html', 'HTML'), (b'text/plain', 'Text'), (b'text/css', 'CSS'), (b'text/javascript', 'JavaScript'), (b'text/csv', 'CSV'), (b'text/xml', 'XML'), (b'text/cachemanifest', 'HTML5 Cache Manifest'))), (b'Application (application/*)', ((b'application/xhtml+xml', 'XHTML'), (b'application/javascript', 'JavaScript'), (b'application/json', 'JSON')))])),
                ('cacheable', models.BooleanField(default=True, verbose_name='cachable')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('site', models.ManyToManyField(default=[1], to='sites.Site')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'template',
                'verbose_name_plural': 'templates',
            },
        ),
        migrations.AddField(
            model_name='resource',
            name='type',
            field=models.ForeignKey(related_name='resources', to='warthog.ResourceType'),
        ),
        migrations.AlterUniqueTogether(
            name='resourcetypefield',
            unique_together=set([('resource_type', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='resourcefield',
            unique_together=set([('resource', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('site', 'slug', 'parent')]),
        ),
    ]
