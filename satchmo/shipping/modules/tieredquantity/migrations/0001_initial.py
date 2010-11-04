# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Carrier'
        db.create_table('tieredquantity_carrier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('tieredquantity', ['Carrier'])

        # Adding model 'CarrierTranslation'
        db.create_table('tieredquantity_carriertranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['tieredquantity.Carrier'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('delivery', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('tieredquantity', ['CarrierTranslation'])

        # Adding model 'QuantityTier'
        db.create_table('tieredquantity_quantitytier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tiers', to=orm['tieredquantity.Carrier'])),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('handling', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('tieredquantity', ['QuantityTier'])


    def backwards(self, orm):
        
        # Deleting model 'Carrier'
        db.delete_table('tieredquantity_carrier')

        # Deleting model 'CarrierTranslation'
        db.delete_table('tieredquantity_carriertranslation')

        # Deleting model 'QuantityTier'
        db.delete_table('tieredquantity_quantitytier')


    models = {
        'tieredquantity.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'tieredquantity.carriertranslation': {
            'Meta': {'object_name': 'CarrierTranslation'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['tieredquantity.Carrier']"}),
            'delivery': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tieredquantity.quantitytier': {
            'Meta': {'object_name': 'QuantityTier'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tiers'", 'to': "orm['tieredquantity.Carrier']"}),
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'handling': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['tieredquantity']
