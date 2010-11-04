# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Carrier'
        db.create_table('tieredweightzone_carrier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('tieredweightzone', ['Carrier'])

        # Adding model 'CarrierTranslation'
        db.create_table('tieredweightzone_carriertranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['tieredweightzone.Carrier'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('delivery', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('tieredweightzone', ['CarrierTranslation'])

        # Adding model 'Zone'
        db.create_table('tieredweightzone_zone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('tieredweightzone', ['Zone'])

        # Adding M2M table for field continent on 'Zone'
        db.create_table('tieredweightzone_zone_continent', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('zone', models.ForeignKey(orm['tieredweightzone.zone'], null=False)),
            ('continent', models.ForeignKey(orm['l10n.continent'], null=False))
        ))
        db.create_unique('tieredweightzone_zone_continent', ['zone_id', 'continent_id'])

        # Adding M2M table for field country on 'Zone'
        db.create_table('tieredweightzone_zone_country', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('zone', models.ForeignKey(orm['tieredweightzone.zone'], null=False)),
            ('country', models.ForeignKey(orm['l10n.country'], null=False))
        ))
        db.create_unique('tieredweightzone_zone_country', ['zone_id', 'country_id'])

        # Adding model 'ZoneTranslation'
        db.create_table('tieredweightzone_zonetranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['tieredweightzone.Zone'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('tieredweightzone', ['ZoneTranslation'])

        # Adding model 'WeightTier'
        db.create_table('tieredweightzone_weighttier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carrier', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tiers', to=orm['tieredweightzone.Carrier'])),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tiers', to=orm['tieredweightzone.Zone'])),
            ('min_weight', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('tieredweightzone', ['WeightTier'])


    def backwards(self, orm):
        
        # Deleting model 'Carrier'
        db.delete_table('tieredweightzone_carrier')

        # Deleting model 'CarrierTranslation'
        db.delete_table('tieredweightzone_carriertranslation')

        # Deleting model 'Zone'
        db.delete_table('tieredweightzone_zone')

        # Removing M2M table for field continent on 'Zone'
        db.delete_table('tieredweightzone_zone_continent')

        # Removing M2M table for field country on 'Zone'
        db.delete_table('tieredweightzone_zone_country')

        # Deleting model 'ZoneTranslation'
        db.delete_table('tieredweightzone_zonetranslation')

        # Deleting model 'WeightTier'
        db.delete_table('tieredweightzone_weighttier')


    models = {
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
        'tieredweightzone.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'tieredweightzone.carriertranslation': {
            'Meta': {'object_name': 'CarrierTranslation'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['tieredweightzone.Carrier']"}),
            'delivery': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tieredweightzone.weighttier': {
            'Meta': {'object_name': 'WeightTier'},
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
            'country': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'country'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['l10n.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'tieredweightzone.zonetranslation': {
            'Meta': {'object_name': 'ZoneTranslation'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['tieredweightzone.Zone']"})
        }
    }

    complete_apps = ['tieredweightzone']
