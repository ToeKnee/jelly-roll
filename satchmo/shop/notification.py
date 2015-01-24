try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

import logging
from socket import error as SocketError
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader, Context
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from smtplib import SMTPRecipientsRefused

log = logging.getLogger(__name__)

def order_success_listener(order=None, **kwargs):
    """Listen for order_success signal, and send confirmations"""
    if order:
        send_order_confirmation(order)
        send_order_notice(order)

def send_order_confirmation(new_order, template='email/order_complete.txt'):
    """Send an order confirmation mail to the customer.
    """
    from satchmo.shop.models import Config

    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email
    t = loader.get_template(template)
    c = Context({'order': new_order, 'shop_config': shop_config})
    subject = _("Thank you for your order from %(shop_name)s (Order id: %(order_id)s)") % {'shop_name' : shop_config.store_name, 'order_id' : new_order.id }

    try:
        customer_email = new_order.contact.email
        body = t.render(c)
        message = EmailMessage(subject, body, shop_email, [customer_email])
        message.send()

    except (SocketError, SMTPRecipientsRefused), e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', customer_email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')

def send_order_update_notice(order_status, template='email/order_status_changed.txt'):
    """Send an email to the customer when the status changes.
    """
    from satchmo.shop.models import Config

    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email
    t = loader.get_template(template)
    c = Context({'order': order_status.order, 'shop_config': shop_config, 'status': order_status, 'notes': order_status.notes})
    subject = _("Your %(shop_name)s order has been updated. Status: %(status)s (Order id: %(order_id)s)") % {'shop_name' : shop_config.store_name, 'status': order_status, 'order_id' : order_status.order.id }

    try:
        customer_email = order_status.order.contact.email
        body = t.render(c)
        message = EmailMessage(subject, body, shop_email, [customer_email])
        message.send()

    except (SocketError, SMTPRecipientsRefused), e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', customer_email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')


def send_order_notice(new_order, template='email/order_placed_notice.txt'):
    """Send an order confirmation mail to the owner.
    """
    from satchmo.shop.models import Config
    
    if config_value("PAYMENT", "ORDER_EMAIL_OWNER"):
        shop_config = Config.objects.get_current()
        shop_email = shop_config.store_email
        t = loader.get_template(template)
        c = Context({'order': new_order, 'shop_config': shop_config})
        subject = _("New order on %(shop_name)s") % {'shop_name' : shop_config.store_name}
        
        eddresses = [shop_email, ]
        more = config_value("PAYMENT", "ORDER_EMAIL_EXTRA")
        if more:
            more = [m.strip() for m in more.split(',')]
            for m in more:
                if not m in eddresses:
                    eddresses.append(m)
                    
        eddresses = [e for e in eddresses if e]
        if not eddresses:
            log.warn("No shop owner email specified, skipping owner_email")
            return

        try:
            body = t.render(c)
            message = EmailMessage(subject, body, shop_email, eddresses)
            message.send()

        except (SocketError, SMTPRecipientsRefused), e:
            if settings.DEBUG:
                log.error('Error sending mail: %s' % e)
                log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', ",".join(eddresses), subject, body)
            else:
                log.fatal('Error sending mail: %s' % e)
                raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')
