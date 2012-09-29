# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ShippingDiscount'
        db.create_table('tieredweightzone_shippingdiscount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shipping_discount', to=orm['tieredweightzone.Carrier'])),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shipping_discount', to=orm['tieredweightzone.Zone'])),
            ('percentage', self.gf('django.db.models.fields.IntegerField')()),
            ('minimum_order_value', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('message_to_customer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('tieredweightzone', ['ShippingDiscount'])


    def backwards(self, orm):
        
        # Deleting model 'ShippingDiscount'
        db.delete_table('tieredweightzone_shippingdiscount')


    models = {
        'l10n.continent': {
            'Meta': {'object_name': 'Continent'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'l10n.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'admin_area': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['l10n.Continent']", 'to_field': "'code'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'iso3_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'tieredweightzone.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'tieredweightzone.carriertranslation': {
            'Meta': {'ordering': "('languagecode', 'name')", 'object_name': 'CarrierTranslation'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['tieredweightzone.Carrier']"}),
            'delivery': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tieredweightzone.shippingdiscount': {
            'Meta': {'object_name': 'ShippingDiscount'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shipping_discount'", 'to': "orm['tieredweightzone.Carrier']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_to_customer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'minimum_order_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'percentage': ('django.db.models.fields.IntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shipping_discount'", 'to': "orm['tieredweightzone.Zone']"})
        },
        'tieredweightzone.weighttier': {
            'Meta': {'ordering': "('zone', 'carrier', 'price')", 'object_name': 'WeightTier'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tiers'", 'to': "orm['tieredweightzone.Carrier']"}),
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tiers'", 'to': "orm['tieredweightzone.Zone']"})
        },
        'tieredweightzone.zone': {
            'Meta': {'object_name': 'Zone'},
            'continent': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'continent'", 'symmetrical': 'False', 'to': "orm['l10n.Continent']"}),
            'country': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'zone'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['l10n.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'tieredweightzone.zonetranslation': {
            'Meta': {'ordering': "('languagecode', 'name')", 'object_name': 'ZoneTranslation'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['tieredweightzone.Zone']"})
        }
    }

    complete_apps = ['tieredweightzone']
