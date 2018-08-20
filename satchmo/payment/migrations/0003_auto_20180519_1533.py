# Generated by Django 2.0.5 on 2018-05-19 15:33

from django.db import migrations, models
import django.db.models.deletion
import satchmo.payment.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_creditcarddetail_orderpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcarddetail',
            name='orderpayment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='creditcards', to='shop.OrderPayment'),
        ),
        migrations.AlterField(
            model_name='paymentoption',
            name='optionName',
            field=satchmo.payment.fields.PaymentChoiceCharField(help_text='The class name as defined in payment.py', max_length=20, unique=True),
        ),
    ]