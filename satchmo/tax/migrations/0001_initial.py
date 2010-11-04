# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TaxClass'
        db.create_table('tax_taxclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('tax', ['TaxClass'])

        # Adding model 'TaxRate'
        db.create_table('tax_taxrate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('taxClass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tax.TaxClass'])),
            ('taxZone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['l10n.AdminArea'], null=True, blank=True)),
            ('taxCountry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['l10n.Country'], null=True, blank=True)),
            ('percentage', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=6)),
        ))
        db.send_create_signal('tax', ['TaxRate'])


    def backwards(self, orm):
        
        # Deleting model 'TaxClass'
        db.delete_table('tax_taxclass')

        # Deleting model 'TaxRate'
        db.delete_table('tax_taxrate')


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
        },
        'tax.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'tax.taxrate': {
            'Meta': {'object_name': 'TaxRate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '6'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.TaxClass']"}),
            'taxCountry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['l10n.Country']", 'null': 'True', 'blank': 'True'}),
            'taxZone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['l10n.AdminArea']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tax']
