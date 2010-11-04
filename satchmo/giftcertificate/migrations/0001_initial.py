# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GiftCertificate'
        db.create_table('giftcertificate_giftcertificate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='giftcertificates', null=True, to=orm['shop.Order'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('purchased_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='giftcertificates_purchased', null=True, to=orm['contact.Contact'])),
            ('date_added', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('recipient_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('start_balance', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('giftcertificate', ['GiftCertificate'])

        # Adding model 'GiftCertificateUsage'
        db.create_table('giftcertificate_giftcertificateusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('balance_used', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('orderpayment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.OrderPayment'], null=True)),
            ('used_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='giftcertificates_used', null=True, to=orm['contact.Contact'])),
            ('giftcertificate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='usages', to=orm['giftcertificate.GiftCertificate'])),
        ))
        db.send_create_signal('giftcertificate', ['GiftCertificateUsage'])

        # Adding model 'GiftCertificateProduct'
        db.create_table('giftcertificate_giftcertificateproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('giftcertificate', ['GiftCertificateProduct'])


    def backwards(self, orm):
        
        # Deleting model 'GiftCertificate'
        db.delete_table('giftcertificate_giftcertificate')

        # Deleting model 'GiftCertificateUsage'
        db.delete_table('giftcertificate_giftcertificateusage')

        # Deleting model 'GiftCertificateProduct'
        db.delete_table('giftcertificate_giftcertificateproduct')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contact.contact': {
            'Meta': {'object_name': 'Contact'},
            'create_date': ('django.db.models.fields.DateField', [], {}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Organization']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'contact.organization': {
            'Meta': {'object_name': 'Organization'},
            'create_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'giftcertificate.giftcertificate': {
            'Meta': {'object_name': 'GiftCertificate'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'giftcertificates'", 'null': 'True', 'to': "orm['shop.Order']"}),
            'purchased_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'giftcertificates_purchased'", 'null': 'True', 'to': "orm['contact.Contact']"}),
            'recipient_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'start_balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'giftcertificate.giftcertificateproduct': {
            'Meta': {'object_name': 'GiftCertificateProduct'},
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'giftcertificate.giftcertificateusage': {
            'Meta': {'object_name': 'GiftCertificateUsage'},
            'balance_used': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'giftcertificate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'usages'", 'to': "orm['giftcertificate.GiftCertificate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'orderpayment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.OrderPayment']", 'null': 'True'}),
            'usage_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'used_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'giftcertificates_used'", 'null': 'True', 'to': "orm['contact.Contact']"})
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
            'date_added': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2010, 11, 4, 13, 26, 43, 855970)'}),
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
        'shop.order': {
            'Meta': {'object_name': 'Order'},
            'bill_addressee': ('django.db.models.fields.CharField', [], {'max_length': '61', 'blank': 'True'}),
            'bill_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'bill_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bill_country'", 'blank': 'True', 'to': "orm['l10n.Country']"}),
            'bill_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'bill_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'bill_street1': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'bill_street2': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contact.Contact']"}),
            'discount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ship_addressee': ('django.db.models.fields.CharField', [], {'max_length': '61', 'blank': 'True'}),
            'ship_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ship_country'", 'blank': 'True', 'to': "orm['l10n.Country']"}),
            'ship_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'ship_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_street1': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'ship_street2': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'shipping_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'shipping_description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipping_discount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'shipping_model': ('satchmo.shipping.fields.ShippingChoiceCharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_status'", 'null': 'True', 'to': "orm['shop.OrderStatus']"}),
            'sub_total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 11, 4, 13, 26, 43, 902617)'}),
            'total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'})
        },
        'shop.orderpayment': {
            'Meta': {'object_name': 'OrderPayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['shop.Order']"}),
            'payment': ('satchmo.payment.fields.PaymentChoiceCharField', [], {'max_length': '25', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 11, 4, 13, 26, 43, 908639)'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'})
        },
        'shop.orderstatus': {
            'Meta': {'object_name': 'OrderStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Order']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Status']"}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 11, 4, 13, 26, 43, 907731)'})
        },
        'shop.status': {
            'Meta': {'object_name': 'Status'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notify': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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

    complete_apps = ['giftcertificate']
