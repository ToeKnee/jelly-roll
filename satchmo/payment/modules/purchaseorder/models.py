from . import config
from decimal import Decimal

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

from satchmo.currency.utils import money_format
from satchmo.shop.models import Order


class PurchaseOrder(models.Model):
    po_number = models.CharField(_('Customer PO Number'), max_length=20)
    order = models.ForeignKey(Order)
    balance = models.DecimalField(
        _("Outstanding Balance"),
        max_digits=18, decimal_places=10, blank=True, null=True
    )
    paydate = models.DateField(_('Paid on'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)

    def __unicode__(self):
        return "PO: #%s" % self.po_number

    def balance_due(self):
        if self.balance:
            b = self.balance
        else:
            b = Decimal('0.00')

        return money_format(b, self.order.currency.iso_4217_code)

    def order_link(self):
        return mark_safe('<a href="/admin/shop/order/%i/">%s #%i (%s)</a>' % (
            self.order.id,
            ugettext('Order'),
            self.order.id,
            money_format(self.order.total, self.order.currency.iso_4217_code)
        ))
    order_link.allow_tags = True

    def save(self, *args, **kwargs):
        if self.balance is None:
            self.balance = self.order.balance
        super(PurchaseOrder, self).save(*args, **kwargs)
