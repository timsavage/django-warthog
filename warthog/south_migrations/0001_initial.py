# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Template'
        db.create_table('warthog_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('mime_type', self.gf('django.db.models.fields.CharField')(default='text/html', max_length=25)),
            ('cacheable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('warthog', ['Template'])

        # Adding model 'ResourceType'
        db.create_table('warthog_resourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('default_template', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('warthog', ['ResourceType'])

        # Adding model 'ResourceTypeField'
        db.create_table('warthog_resourcetypefield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['warthog.ResourceType'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('label_raw', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('warthog', ['ResourceTypeField'])

        # Adding unique constraint on 'ResourceTypeField', fields ['resource_type', 'code']
        db.create_unique('warthog_resourcetypefield', ['resource_type_id', 'code'])

        # Adding model 'Resource'
        db.create_table('warthog_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'resources', to=orm['warthog.ResourceType'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('uri_path', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=500, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('unpublish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['warthog.Resource'], null=True, on_delete=models.PROTECT, blank=True)),
            ('menu_title_raw', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('menu_class', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('hide_from_menu', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('warthog', ['Resource'])

        # Adding unique constraint on 'Resource', fields ['uri_path', 'published']
        db.create_unique('warthog_resource', ['uri_path', 'published'])

        # Adding model 'ResourceField'
        db.create_table('warthog_resourcefield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['warthog.Resource'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('warthog', ['ResourceField'])

        # Adding unique constraint on 'ResourceField', fields ['resource', 'code']
        db.create_unique('warthog_resourcefield', ['resource_id', 'code'])


    def backwards(self, orm):
        # Removing unique constraint on 'ResourceField', fields ['resource', 'code']
        db.delete_unique('warthog_resourcefield', ['resource_id', 'code'])

        # Removing unique constraint on 'Resource', fields ['uri_path', 'published']
        db.delete_unique('warthog_resource', ['uri_path', 'published'])

        # Removing unique constraint on 'ResourceTypeField', fields ['resource_type', 'code']
        db.delete_unique('warthog_resourcetypefield', ['resource_type_id', 'code'])

        # Deleting model 'Template'
        db.delete_table('warthog_template')

        # Deleting model 'ResourceType'
        db.delete_table('warthog_resourcetype')

        # Deleting model 'ResourceTypeField'
        db.delete_table('warthog_resourcetypefield')

        # Deleting model 'Resource'
        db.delete_table('warthog_resource')

        # Deleting model 'ResourceField'
        db.delete_table('warthog_resourcefield')


    models = {
        'warthog.resource': {
            'Meta': {'ordering': "['order', 'uri_path', 'title']", 'unique_together': "(('uri_path', 'published'),)", 'object_name': 'Resource'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_from_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu_class': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'menu_title_raw': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['warthog.Resource']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'resources'", 'to': "orm['warthog.ResourceType']"}),
            'unpublish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uri_path': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '500', 'blank': 'True'})
        },
        'warthog.resourcefield': {
            'Meta': {'unique_together': "(('resource', 'code'),)", 'object_name': 'ResourceField'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['warthog.Resource']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'warthog.resourcetype': {
            'Meta': {'object_name': 'ResourceType'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_template': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'warthog.resourcetypefield': {
            'Meta': {'unique_together': "(('resource_type', 'code'),)", 'object_name': 'ResourceTypeField'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_raw': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['warthog.ResourceType']"})
        },
        'warthog.template': {
            'Meta': {'ordering': "['name']", 'object_name': 'Template'},
            'cacheable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'default': "'text/html'", 'max_length': '25'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['warthog']