# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RawItem'
        db.create_table('supplier_rawitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('supplier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contact.Organization'])),
            ('supplier_num', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('unit_cost', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('inventory', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('supplier', ['RawItem'])

        # Adding model 'SupplierOrder'
        db.create_table('supplier_supplierorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('supplier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contact.Organization'])),
            ('date_created', self.gf('django.db.models.fields.DateField')()),
            ('order_sub_total', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('order_shipping', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('order_tax', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('order_notes', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('order_total', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('supplier', ['SupplierOrder'])

        # Adding model 'SupplierOrderItem'
        db.create_table('supplier_supplierorderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supplier.SupplierOrder'])),
            ('line_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supplier.RawItem'])),
            ('line_item_quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('line_item_total', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('supplier', ['SupplierOrderItem'])

        # Adding model 'SupplierOrderStatus'
        db.create_table('supplier_supplierorderstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['supplier.SupplierOrder'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('supplier', ['SupplierOrderStatus'])


    def backwards(self, orm):
        
        # Deleting model 'RawItem'
        db.delete_table('supplier_rawitem')

        # Deleting model 'SupplierOrder'
        db.delete_table('supplier_supplierorder')

        # Deleting model 'SupplierOrderItem'
        db.delete_table('supplier_supplierorderitem')

        # Deleting model 'SupplierOrderStatus'
        db.delete_table('supplier_supplierorderstatus')


    models = {
        'contact.organization': {
            'Meta': {'object_name': 'Organization'},
            'create_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'supplier.rawitem': {
            'Meta': {'object_name': 'RawItem'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory': ('django.db.models.fields.IntegerField', [], {}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Organization']"}),
            'supplier_num': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'unit_cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'supplier.supplierorder': {
            'Meta': {'object_name': 'SupplierOrder'},
            'date_created': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_notes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'order_shipping': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'order_sub_total': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'order_tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'order_total': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Organization']"})
        },
        'supplier.supplierorderitem': {
            'Meta': {'object_name': 'SupplierOrderItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supplier.RawItem']"}),
            'line_item_quantity': ('django.db.models.fields.IntegerField', [], {}),
            'line_item_total': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supplier.SupplierOrder']"})
        },
        'supplier.supplierorderstatus': {
            'Meta': {'object_name': 'SupplierOrderStatus'},
            'date': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['supplier.SupplierOrder']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        }
    }

    complete_apps = ['supplier']
