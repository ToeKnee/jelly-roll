from smtplib import SMTPRecipientsRefused
from socket import error as SocketError

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader
from django.utils.translation import ugettext as _
from django.utils.text import slugify

from satchmo.configuration.functions import config_value

import logging
log = logging.getLogger(__name__)


def send_order_update(order_status):
    """Send an email to the customer when the status changes.
    """
    from satchmo.shop.models import Config

    # If the order_status shouldn't notify, fail early
    if order_status.status.notify is False:
        return None

    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email

    email_slug = slugify(order_status.status.status)

    text_templates = [
        'email/order/status/{slug}.txt'.format(
            slug=email_slug,
        ),
        'email/order/status/generic.txt'
    ]
    text_template = loader.select_template(text_templates)
    html_templates = [
        'email/order/status/{slug}.html'.format(
            slug=email_slug,
        ),
        'email/order/status/generic.html'
    ]

    html_template = loader.select_template(html_templates)
    context = {
        'order': order_status.order,
        'shop_config': shop_config,
        'status': order_status,
        'notes': order_status.notes
    }

    subject = _("Your {shop_name} order #{order_id} has been updated - {status}").format(
        shop_name=shop_config.store_name,
        status=order_status,
        order_id=order_status.order_id,
    )

    customer_email = order_status.order.contact.email
    body = text_template.render(context)
    message = EmailMultiAlternatives(
        subject,
        body,
        shop_email,
        [customer_email],
    )

    html_body = html_template.render(context)
    message.attach_alternative(html_body, "text/html")

    try:
        message.send()
    except (SocketError, SMTPRecipientsRefused) as e:
        if settings.DEBUG:
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s',
                     customer_email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError(
                'Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')


def send_owner_order_notice(new_order, template='email/order/placed_notice.txt'):
    """Send an order confirmation mail to the owner.
    """
    from satchmo.shop.models import Config

    if config_value("PAYMENT", "ORDER_EMAIL_OWNER"):
        shop_config = Config.objects.get_current()
        shop_email = shop_config.store_email
        t = loader.get_template(template)
        c = {'order': new_order, 'shop_config': shop_config}
        subject = _("New order on {shop_name}").format(
            shop_name=shop_config.store_name,
        )

        eddresses = [shop_email, ]
        more = config_value("PAYMENT", "ORDER_EMAIL_EXTRA")
        if more:
            more = [m.strip() for m in more.split(',')]
            for m in more:
                if m not in eddresses:
                    eddresses.append(m)

        eddresses = [e for e in eddresses if e]
        if not eddresses:
            log.warn("No shop owner email specified, skipping owner_email")
            return

        try:
            body = t.render(c)
            message = EmailMessage(subject, body, shop_email, eddresses)
            message.send()

        except (SocketError, SMTPRecipientsRefused) as e:
            if settings.DEBUG:
                log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s',
                         ",".join(eddresses), subject, body)
            else:
                log.fatal('Error sending mail: %s' % e)
                raise IOError(
                    'Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')
