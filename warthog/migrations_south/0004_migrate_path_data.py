# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for resource in orm.Resource.objects.all():
            if resource.parent is None:
                resource.slug = ''
            else:
                resource.slug = resource.uri_path[len(resource.parent.uri_path):].strip('/')
            resource.save()

    def backwards(self, orm):
        pass # Note required

    models = {
        'warthog.resource': {
            'Meta': {'ordering': "['order', 'uri_path', 'title']", 'object_name': 'Resource'},
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
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'resources'", 'to': "orm['warthog.ResourceType']"}),
            'unpublish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uri_path': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '500', 'blank': 'True'})
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
            'child_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['warthog.ResourceType']", 'symmetrical': 'False', 'blank': 'True'}),
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
    symmetrical = True
