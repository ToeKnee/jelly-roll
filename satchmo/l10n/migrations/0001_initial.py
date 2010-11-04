# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Continent'
        db.create_table('l10n_continent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('l10n', ['Continent'])

        # Adding model 'Country'
        db.create_table('l10n_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iso2_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('printable_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('iso3_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('numcode', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('continent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['l10n.Continent'], to_field='code')),
            ('admin_area', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
        ))
        db.send_create_signal('l10n', ['Country'])

        # Adding model 'AdminArea'
        db.create_table('l10n_adminarea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['l10n.Country'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('l10n', ['AdminArea'])


    def backwards(self, orm):
        
        # Deleting model 'Continent'
        db.delete_table('l10n_continent')

        # Deleting model 'Country'
        db.delete_table('l10n_country')

        # Deleting model 'AdminArea'
        db.delete_table('l10n_adminarea')


    models = {
        'l10n.adminarea': {
            'Meta': {'object_name': 'AdminArea'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['l10n.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'l10n.continent': {
            'Meta': {'object_name': 'Continent'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'l10n.country': {
            'Meta': {'object_name': 'Country'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'admin_area': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['l10n.Continent']", 'to_field': "'code'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'iso3_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['l10n']
