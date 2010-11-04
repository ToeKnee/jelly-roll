# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Carrier'
        db.create_table('tiered_carrier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('tiered', ['Carrier'])

        # Adding model 'CarrierTranslation'
        db.create_table('tiered_carriertranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['tiered.Carrier'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('delivery', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('tiered', ['CarrierTranslation'])

        # Adding model 'ShippingTier'
        db.create_table('tiered_shippingtier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tiers', to=orm['tiered.Carrier'])),
            ('min_total', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('tiered', ['ShippingTier'])


    def backwards(self, orm):
        
        # Deleting model 'Carrier'
        db.delete_table('tiered_carrier')

        # Deleting model 'CarrierTranslation'
        db.delete_table('tiered_carriertranslation')

        # Deleting model 'ShippingTier'
        db.delete_table('tiered_shippingtier')


    models = {
        'tiered.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'tiered.carriertranslation': {
            'Meta': {'object_name': 'CarrierTranslation'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['tiered.Carrier']"}),
            'delivery': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tiered.shippingtier': {
            'Meta': {'object_name': 'ShippingTier'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tiers'", 'to': "orm['tiered.Carrier']"}),
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_total': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['tiered']
