# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('product_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child', null=True, to=orm['product.Category'])),
            ('meta', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('product', ['Category'])

        # Adding M2M table for field related_categories on 'Category'
        db.create_table('product_category_related_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_category', models.ForeignKey(orm['product.category'], null=False)),
            ('to_category', models.ForeignKey(orm['product.category'], null=False))
        ))
        db.create_unique('product_category_related_categories', ['from_category_id', 'to_category_id'])

        # Adding model 'CategoryTranslation'
        db.create_table('product_categorytranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.Category'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['CategoryTranslation'])

        # Adding unique constraint on 'CategoryTranslation', fields ['category', 'languagecode', 'version']
        db.create_unique('product_categorytranslation', ['category_id', 'languagecode', 'version'])

        # Adding model 'CategoryImage'
        db.create_table('product_categoryimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='images', null=True, to=orm['product.Category'])),
            ('picture', self.gf('satchmo.thumbnail.field.ImageWithThumbnailField')(max_length=200)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('sort', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('product', ['CategoryImage'])

        # Adding unique constraint on 'CategoryImage', fields ['category', 'sort']
        db.create_unique('product_categoryimage', ['category_id', 'sort'])

        # Adding model 'CategoryImageTranslation'
        db.create_table('product_categoryimagetranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('categoryimage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.CategoryImage'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['CategoryImageTranslation'])

        # Adding unique constraint on 'CategoryImageTranslation', fields ['categoryimage', 'languagecode', 'version']
        db.create_unique('product_categoryimagetranslation', ['categoryimage_id', 'languagecode', 'version'])

        # Adding model 'OptionGroup'
        db.create_table('product_optiongroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('product', ['OptionGroup'])

        # Adding model 'OptionGroupTranslation'
        db.create_table('product_optiongrouptranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('optiongroup', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.OptionGroup'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['OptionGroupTranslation'])

        # Adding unique constraint on 'OptionGroupTranslation', fields ['optiongroup', 'languagecode', 'version']
        db.create_unique('product_optiongrouptranslation', ['optiongroup_id', 'languagecode', 'version'])

        # Adding model 'Option'
        db.create_table('product_option', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.OptionGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('price_change', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=6, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('product', ['Option'])

        # Adding unique constraint on 'Option', fields ['option_group', 'value']
        db.create_unique('product_option', ['option_group_id', 'value'])

        # Adding model 'OptionTranslation'
        db.create_table('product_optiontranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.Option'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['OptionTranslation'])

        # Adding unique constraint on 'OptionTranslation', fields ['option', 'languagecode', 'version']
        db.create_unique('product_optiontranslation', ['option_id', 'languagecode', 'version'])

        # Adding model 'Product'
        db.create_table('product_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=80, blank=True)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('short_description', self.gf('django.db.models.fields.TextField')(default='', max_length=200, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('items_in_stock', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('meta', self.gf('django.db.models.fields.TextField')(max_length=200, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2010, 11, 4))),
            ('date_updated', self.gf('django.db.models.fields.DateField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('weight_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('length_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('width_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('height_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('total_sold', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('taxClass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tax.TaxClass'], null=True, blank=True)),
            ('shipclass', self.gf('django.db.models.fields.CharField')(default='YES', max_length=10)),
            ('ingredients', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.IngredientsList'], null=True, blank=True)),
            ('instructions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Instruction'], null=True, blank=True)),
            ('precautions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Precaution'], null=True, blank=True)),
        ))
        db.send_create_signal('product', ['Product'])

        # Adding unique constraint on 'Product', fields ['site', 'sku']
        db.create_unique('product_product', ['site_id', 'sku'])

        # Adding unique constraint on 'Product', fields ['site', 'slug']
        db.create_unique('product_product', ['site_id', 'slug'])

        # Adding M2M table for field category on 'Product'
        db.create_table('product_product_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['product.product'], null=False)),
            ('category', models.ForeignKey(orm['product.category'], null=False))
        ))
        db.create_unique('product_product_category', ['product_id', 'category_id'])

        # Adding M2M table for field related_items on 'Product'
        db.create_table('product_product_related_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm['product.product'], null=False)),
            ('to_product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('product_product_related_items', ['from_product_id', 'to_product_id'])

        # Adding M2M table for field also_purchased on 'Product'
        db.create_table('product_product_also_purchased', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm['product.product'], null=False)),
            ('to_product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('product_product_also_purchased', ['from_product_id', 'to_product_id'])

        # Adding model 'ProductTranslation'
        db.create_table('product_producttranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.Product'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('short_description', self.gf('django.db.models.fields.TextField')(default='', max_length=200, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['ProductTranslation'])

        # Adding unique constraint on 'ProductTranslation', fields ['product', 'languagecode', 'version']
        db.create_unique('product_producttranslation', ['product_id', 'languagecode', 'version'])

        # Adding model 'CustomProduct'
        db.create_table('product_customproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('downpayment', self.gf('django.db.models.fields.IntegerField')(default=20)),
            ('deferred_shipping', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('product', ['CustomProduct'])

        # Adding M2M table for field option_group on 'CustomProduct'
        db.create_table('product_customproduct_option_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customproduct', models.ForeignKey(orm['product.customproduct'], null=False)),
            ('optiongroup', models.ForeignKey(orm['product.optiongroup'], null=False))
        ))
        db.create_unique('product_customproduct_option_group', ['customproduct_id', 'optiongroup_id'])

        # Adding model 'CustomTextField'
        db.create_table('product_customtextfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('products', self.gf('django.db.models.fields.related.ForeignKey')(related_name='custom_text_fields', to=orm['product.CustomProduct'])),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
            ('price_change', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=6, blank=True)),
        ))
        db.send_create_signal('product', ['CustomTextField'])

        # Adding model 'CustomTextFieldTranslation'
        db.create_table('product_customtextfieldtranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customtextfield', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.CustomTextField'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['CustomTextFieldTranslation'])

        # Adding unique constraint on 'CustomTextFieldTranslation', fields ['customtextfield', 'languagecode', 'version']
        db.create_unique('product_customtextfieldtranslation', ['customtextfield_id', 'languagecode', 'version'])

        # Adding model 'ConfigurableProduct'
        db.create_table('product_configurableproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('create_subs', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('product', ['ConfigurableProduct'])

        # Adding M2M table for field option_group on 'ConfigurableProduct'
        db.create_table('product_configurableproduct_option_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('configurableproduct', models.ForeignKey(orm['product.configurableproduct'], null=False)),
            ('optiongroup', models.ForeignKey(orm['product.optiongroup'], null=False))
        ))
        db.create_unique('product_configurableproduct_option_group', ['configurableproduct_id', 'optiongroup_id'])

        # Adding model 'DownloadableProduct'
        db.create_table('product_downloadableproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('num_allowed_downloads', self.gf('django.db.models.fields.IntegerField')()),
            ('expire_minutes', self.gf('django.db.models.fields.IntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['DownloadableProduct'])

        # Adding model 'SubscriptionProduct'
        db.create_table('product_subscriptionproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('recurring', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('recurring_times', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('expire_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('expire_unit', self.gf('django.db.models.fields.CharField')(default='DAY', max_length=5)),
            ('is_shippable', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
        ))
        db.send_create_signal('product', ['SubscriptionProduct'])

        # Adding model 'Trial'
        db.create_table('product_trial', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.SubscriptionProduct'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2)),
            ('expire_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('product', ['Trial'])

        # Adding model 'ProductVariation'
        db.create_table('product_productvariation', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.ConfigurableProduct'])),
        ))
        db.send_create_signal('product', ['ProductVariation'])

        # Adding M2M table for field options on 'ProductVariation'
        db.create_table('product_productvariation_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('productvariation', models.ForeignKey(orm['product.productvariation'], null=False)),
            ('option', models.ForeignKey(orm['product.option'], null=False))
        ))
        db.create_unique('product_productvariation_options', ['productvariation_id', 'option_id'])

        # Adding model 'ProductPriceLookup'
        db.create_table('product_productpricelookup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('siteid', self.gf('django.db.models.fields.IntegerField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('parentid', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('productslug', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=6)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('discountable', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('items_in_stock', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('product', ['ProductPriceLookup'])

        # Adding model 'ProductAttribute'
        db.create_table('product_productattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('product', ['ProductAttribute'])

        # Adding model 'Price'
        db.create_table('product_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=6)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('product', ['Price'])

        # Adding unique constraint on 'Price', fields ['product', 'quantity', 'expires']
        db.create_unique('product_price', ['product_id', 'quantity', 'expires'])

        # Adding model 'ProductImage'
        db.create_table('product_productimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'], null=True, blank=True)),
            ('picture', self.gf('satchmo.thumbnail.field.ImageWithThumbnailField')(max_length=200)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('sort', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('product', ['ProductImage'])

        # Adding model 'ProductImageTranslation'
        db.create_table('product_productimagetranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('productimage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.ProductImage'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('product', ['ProductImageTranslation'])

        # Adding unique constraint on 'ProductImageTranslation', fields ['productimage', 'languagecode', 'version']
        db.create_unique('product_productimagetranslation', ['productimage_id', 'languagecode', 'version'])

        # Adding model 'IngredientsList'
        db.create_table('product_ingredientslist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ingredients', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('product', ['IngredientsList'])

        # Adding model 'Instruction'
        db.create_table('product_instruction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('instructions', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('product', ['Instruction'])

        # Adding model 'Precaution'
        db.create_table('product_precaution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('precautions', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('product', ['Precaution'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('product_category')

        # Removing M2M table for field related_categories on 'Category'
        db.delete_table('product_category_related_categories')

        # Deleting model 'CategoryTranslation'
        db.delete_table('product_categorytranslation')

        # Removing unique constraint on 'CategoryTranslation', fields ['category', 'languagecode', 'version']
        db.delete_unique('product_categorytranslation', ['category_id', 'languagecode', 'version'])

        # Deleting model 'CategoryImage'
        db.delete_table('product_categoryimage')

        # Removing unique constraint on 'CategoryImage', fields ['category', 'sort']
        db.delete_unique('product_categoryimage', ['category_id', 'sort'])

        # Deleting model 'CategoryImageTranslation'
        db.delete_table('product_categoryimagetranslation')

        # Removing unique constraint on 'CategoryImageTranslation', fields ['categoryimage', 'languagecode', 'version']
        db.delete_unique('product_categoryimagetranslation', ['categoryimage_id', 'languagecode', 'version'])

        # Deleting model 'OptionGroup'
        db.delete_table('product_optiongroup')

        # Deleting model 'OptionGroupTranslation'
        db.delete_table('product_optiongrouptranslation')

        # Removing unique constraint on 'OptionGroupTranslation', fields ['optiongroup', 'languagecode', 'version']
        db.delete_unique('product_optiongrouptranslation', ['optiongroup_id', 'languagecode', 'version'])

        # Deleting model 'Option'
        db.delete_table('product_option')

        # Removing unique constraint on 'Option', fields ['option_group', 'value']
        db.delete_unique('product_option', ['option_group_id', 'value'])

        # Deleting model 'OptionTranslation'
        db.delete_table('product_optiontranslation')

        # Removing unique constraint on 'OptionTranslation', fields ['option', 'languagecode', 'version']
        db.delete_unique('product_optiontranslation', ['option_id', 'languagecode', 'version'])

        # Deleting model 'Product'
        db.delete_table('product_product')

        # Removing unique constraint on 'Product', fields ['site', 'sku']
        db.delete_unique('product_product', ['site_id', 'sku'])

        # Removing unique constraint on 'Product', fields ['site', 'slug']
        db.delete_unique('product_product', ['site_id', 'slug'])

        # Removing M2M table for field category on 'Product'
        db.delete_table('product_product_category')

        # Removing M2M table for field related_items on 'Product'
        db.delete_table('product_product_related_items')

        # Removing M2M table for field also_purchased on 'Product'
        db.delete_table('product_product_also_purchased')

        # Deleting model 'ProductTranslation'
        db.delete_table('product_producttranslation')

        # Removing unique constraint on 'ProductTranslation', fields ['product', 'languagecode', 'version']
        db.delete_unique('product_producttranslation', ['product_id', 'languagecode', 'version'])

        # Deleting model 'CustomProduct'
        db.delete_table('product_customproduct')

        # Removing M2M table for field option_group on 'CustomProduct'
        db.delete_table('product_customproduct_option_group')

        # Deleting model 'CustomTextField'
        db.delete_table('product_customtextfield')

        # Deleting model 'CustomTextFieldTranslation'
        db.delete_table('product_customtextfieldtranslation')

        # Removing unique constraint on 'CustomTextFieldTranslation', fields ['customtextfield', 'languagecode', 'version']
        db.delete_unique('product_customtextfieldtranslation', ['customtextfield_id', 'languagecode', 'version'])

        # Deleting model 'ConfigurableProduct'
        db.delete_table('product_configurableproduct')

        # Removing M2M table for field option_group on 'ConfigurableProduct'
        db.delete_table('product_configurableproduct_option_group')

        # Deleting model 'DownloadableProduct'
        db.delete_table('product_downloadableproduct')

        # Deleting model 'SubscriptionProduct'
        db.delete_table('product_subscriptionproduct')

        # Deleting model 'Trial'
        db.delete_table('product_trial')

        # Deleting model 'ProductVariation'
        db.delete_table('product_productvariation')

        # Removing M2M table for field options on 'ProductVariation'
        db.delete_table('product_productvariation_options')

        # Deleting model 'ProductPriceLookup'
        db.delete_table('product_productpricelookup')

        # Deleting model 'ProductAttribute'
        db.delete_table('product_productattribute')

        # Deleting model 'Price'
        db.delete_table('product_price')

        # Removing unique constraint on 'Price', fields ['product', 'quantity', 'expires']
        db.delete_unique('product_price', ['product_id', 'quantity', 'expires'])

        # Deleting model 'ProductImage'
        db.delete_table('product_productimage')

        # Deleting model 'ProductImageTranslation'
        db.delete_table('product_productimagetranslation')

        # Removing unique constraint on 'ProductImageTranslation', fields ['productimage', 'languagecode', 'version']
        db.delete_unique('product_productimagetranslation', ['productimage_id', 'languagecode', 'version'])

        # Deleting model 'IngredientsList'
        db.delete_table('product_ingredientslist')

        # Deleting model 'Instruction'
        db.delete_table('product_instruction')

        # Deleting model 'Precaution'
        db.delete_table('product_precaution')


    models = {
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
        'product.categoryimage': {
            'Meta': {'unique_together': "(('category', 'sort'),)", 'object_name': 'CategoryImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'images'", 'null': 'True', 'to': "orm['product.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('satchmo.thumbnail.field.ImageWithThumbnailField', [], {'max_length': '200'}),
            'sort': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.categoryimagetranslation': {
            'Meta': {'unique_together': "(('categoryimage', 'languagecode', 'version'),)", 'object_name': 'CategoryImageTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'categoryimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CategoryImage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.categorytranslation': {
            'Meta': {'unique_together': "(('category', 'languagecode', 'version'),)", 'object_name': 'CategoryTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.configurableproduct': {
            'Meta': {'object_name': 'ConfigurableProduct'},
            'create_subs': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'option_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.OptionGroup']", 'symmetrical': 'False', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.customproduct': {
            'Meta': {'object_name': 'CustomProduct'},
            'deferred_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'downpayment': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'option_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.OptionGroup']", 'symmetrical': 'False', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.customtextfield': {
            'Meta': {'object_name': 'CustomTextField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'price_change': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_text_fields'", 'to': "orm['product.CustomProduct']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.customtextfieldtranslation': {
            'Meta': {'unique_together': "(('customtextfield', 'languagecode', 'version'),)", 'object_name': 'CustomTextFieldTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'customtextfield': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CustomTextField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.downloadableproduct': {
            'Meta': {'object_name': 'DownloadableProduct'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'expire_minutes': ('django.db.models.fields.IntegerField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'num_allowed_downloads': ('django.db.models.fields.IntegerField', [], {}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
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
        'product.option': {
            'Meta': {'unique_together': "(('option_group', 'value'),)", 'object_name': 'Option'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'option_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.OptionGroup']"}),
            'price_change': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'product.optiongroup': {
            'Meta': {'object_name': 'OptionGroup'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.optiongrouptranslation': {
            'Meta': {'unique_together': "(('optiongroup', 'languagecode', 'version'),)", 'object_name': 'OptionGroupTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'optiongroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.OptionGroup']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.optiontranslation': {
            'Meta': {'unique_together': "(('option', 'languagecode', 'version'),)", 'object_name': 'OptionTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Option']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.precaution': {
            'Meta': {'object_name': 'Precaution'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'precautions': ('django.db.models.fields.TextField', [], {})
        },
        'product.price': {
            'Meta': {'unique_together': "(('product', 'quantity', 'expires'),)", 'object_name': 'Price'},
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '6'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.product': {
            'Meta': {'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'also_purchased_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2010, 11, 4)'}),
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
        'product.productattribute': {
            'Meta': {'object_name': 'ProductAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'product.productimage': {
            'Meta': {'object_name': 'ProductImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('satchmo.thumbnail.field.ImageWithThumbnailField', [], {'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'}),
            'sort': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.productimagetranslation': {
            'Meta': {'unique_together': "(('productimage', 'languagecode', 'version'),)", 'object_name': 'ProductImageTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'productimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.ProductImage']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.productpricelookup': {
            'Meta': {'object_name': 'ProductPriceLookup'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'discountable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.IntegerField', [], {}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'parentid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '6'}),
            'productslug': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'siteid': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.producttranslation': {
            'Meta': {'unique_together': "(('product', 'languagecode', 'version'),)", 'object_name': 'ProductTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Product']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.productvariation': {
            'Meta': {'object_name': 'ProductVariation'},
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Option']", 'symmetrical': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.ConfigurableProduct']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.subscriptionproduct': {
            'Meta': {'object_name': 'SubscriptionProduct'},
            'expire_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expire_unit': ('django.db.models.fields.CharField', [], {'default': "'DAY'", 'max_length': '5'}),
            'is_shippable': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'recurring': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'recurring_times': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'product.trial': {
            'Meta': {'object_name': 'Trial'},
            'expire_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.SubscriptionProduct']"})
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

    complete_apps = ['product']
