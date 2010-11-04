# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Discount'
        db.create_table('discount_discount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('percentage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('automatic', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('allowedUses', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('numUses', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('minOrder', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('startDate', self.gf('django.db.models.fields.DateField')()),
            ('endDate', self.gf('django.db.models.fields.DateField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('freeShipping', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('includeShipping', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('discount', ['Discount'])

        # Adding M2M table for field validProducts on 'Discount'
        db.create_table('discount_discount_validProducts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('discount', models.ForeignKey(orm['discount.discount'], null=False)),
            ('product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('discount_discount_validProducts', ['discount_id', 'product_id'])


    def backwards(self, orm):
        
        # Deleting model 'Discount'
        db.delete_table('discount_discount')

        # Removing M2M table for field validProducts on 'Discount'
        db.delete_table('discount_discount_validProducts')


    models = {
        'discount.discount': {
            'Meta': {'object_name': 'Discount'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allowedUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'automatic': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'endDate': ('django.db.models.fields.DateField', [], {}),
            'freeShipping': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'includeShipping': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'minOrder': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'numUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'startDate': ('django.db.models.fields.DateField', [], {}),
            'validProducts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'})
        },
        'product.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_categories_rel_+'", 'null': 'True', 'to': "orm['product.Category']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.ingredientslist': {
            'Meta': {'object_name': 'IngredientsList'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('django.db.models.fields.TextField', [], {})
        },
        'product.instruction': {
            'Meta': {'object_name': 'Instruction'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {})
        },
        'product.precaution': {
            'Meta': {'object_name': 'Precaution'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'precautions': ('django.db.models.fields.TextField', [], {})
        },
        'product.product': {
            'Meta': {'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'also_purchased_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2010, 11, 4, 13, 24, 6, 795857)'}),
            'date_updated': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'height': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'height_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.IngredientsList']", 'null': 'True', 'blank': 'True'}),
            'instructions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Instruction']", 'null': 'True', 'blank': 'True'}),
            'items_in_stock': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'length_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'precautions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Precaution']", 'null': 'True', 'blank': 'True'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_items_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'shipclass': ('django.db.models.fields.CharField', [], {'default': "'YES'", 'max_length': '10'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'blank': 'True'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.TaxClass']", 'null': 'True', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'total_sold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'width_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tax.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['discount']
