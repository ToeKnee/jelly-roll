from datetime import datetime
from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchmo.configuration.functions import config_get_group
from satchmo.contact.models import Contact
from satchmo.currency.utils import money_format
from satchmo.giftcertificate.utils import generate_certificate_code
from satchmo.payment.utils import record_payment
from satchmo.product.models import Product
from satchmo.shop.models import OrderPayment, Order

import logging

log = logging.getLogger(__name__)

GIFTCODE_KEY = "GIFTCODE"


class GiftCertificateManager(models.Manager):
    def from_order(self, order):
        code = order.get_variable(GIFTCODE_KEY, "")
        log.debug("GiftCert.from_order code=%s", code)
        if code:
            return GiftCertificate.objects.get(
                code__exact=code.value, valid__exact=True
            )
        raise GiftCertificate.DoesNotExist()


class GiftCertificate(models.Model):
    """A Gift Cert which holds value."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="giftcertificates",
        verbose_name=_("Order"),
    )
    code = models.CharField(
        _("Certificate Code"), max_length=100, blank=True, null=True
    )
    purchased_by = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        verbose_name=_("Purchased by"),
        blank=True,
        null=True,
        related_name="giftcertificates_purchased",
    )
    date_added = models.DateField(_("Date added"), null=True, blank=True)
    valid = models.BooleanField(_("Valid"), default=True)
    message = models.TextField(_("Message"), blank=True)
    recipient_email = models.EmailField(_("Email"), blank=True)
    start_balance = models.DecimalField(
        _("Starting Balance"), decimal_places=2, max_digits=8
    )

    objects = GiftCertificateManager()

    def balance(self):
        b = Decimal(self.start_balance)
        for usage in self.usages.all():
            log.info("usage: %s" % usage)
            b = b - Decimal(usage.balance_used)

        return b

    balance = property(balance)

    def apply_to_order(self, order):
        """Apply up to the full amount of the balance of this cert to the order.

        Returns new balance.
        """
        amount = min(order.balance, self.balance)
        log.info(
            "applying %s from giftcert #%i [%s] to order #%i [%s]",
            money_format(amount, order.currency.iso_4217_code),
            self.id,
            money_format(self.balance, order.currency.iso_4217_code),
            order.id,
            money_format(order.balance, order.currency.iso_4217_code),
        )
        config = config_get_group("PAYMENT_GIFTCERTIFICATE")
        orderpayment = record_payment(order, config, amount)
        return self.use(amount, orderpayment=orderpayment)

    def use(self, amount, notes="", orderpayment=None):
        """Use some amount of the gift cert, returning the current balance."""
        u = GiftCertificateUsage(
            notes=notes,
            balance_used=amount,
            orderpayment=orderpayment,
            giftcertificate=self,
        )
        u.save()
        return self.balance

    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_added = datetime.now()
        if not self.code:
            self.code = generate_certificate_code()
        super(GiftCertificate, self).save(*args, **kwargs)

    def __str__(self):
        sb = money_format(self.start_balance, self.order.iso_4217_code)
        b = money_format(self.balance, self.order.iso_4217_code)
        return "Gift Cert: %s/%s" % (sb, b)

    class Meta:
        verbose_name = _("Gift Certificate")
        verbose_name_plural = _("Gift Certificates")


class GiftCertificateUsage(models.Model):
    """Any usage of a Gift Cert is logged with one of these objects."""

    usage_date = models.DateField(_("Date of usage"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    balance_used = models.DecimalField(_("Amount Used"), decimal_places=2, max_digits=8)
    orderpayment = models.ForeignKey(
        OrderPayment,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("Order Payment"),
    )
    used_by = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        verbose_name=_("Used by"),
        blank=True,
        null=True,
        related_name="giftcertificates_used",
    )
    giftcertificate = models.ForeignKey(
        GiftCertificate, on_delete=models.CASCADE, related_name="usages"
    )

    def __str__(self):
        return "GiftCertificateUsage: %s" % self.balance_used

    def save(self, *args, **kwargs):
        if not self.pk:
            self.usage_date = datetime.now()
        super(GiftCertificateUsage, self).save(*args, **kwargs)


class GiftCertificateProduct(models.Model):
    """
    The product model for a Gift Certificate
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), primary_key=True
    )
    is_shippable = False
    discountable = False

    def __str__(self):
        return "GiftCertificateProduct: %s" % self.product.name

    def _get_subtype(self):
        return "GiftCertificateProduct"

    def order_success(self, order, order_item):
        log.debug("Order success called, creating gift certs on order: %s", order)
        message = ""
        email = ""
        for detl in order_item.orderitemdetail_set.all():
            if detl.name == "email":
                email = detl.value
            elif detl.name == "message":
                message = detl.value

        price = order_item.line_item_price
        log.debug("Creating gc for %s", price)
        gc = GiftCertificate(
            order=order,
            start_balance=price,
            purchased_by=order.contact,
            valid=True,
            message=message,
            recipient_email=email,
        )
        gc.save()

    class Meta:
        verbose_name = _("Gift certificate product")
        verbose_name_plural = _("Gift certificate products")
