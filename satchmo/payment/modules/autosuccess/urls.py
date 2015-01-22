from django.conf.urls import patterns

urlpatterns = patterns('satchmo',
                       (r'^$', 'payment.modules.autosuccess.views.one_step', {}, 'AUTOSUCCESS_satchmo_checkout-step2'),
                       (r'^success/$', 'payment.views.checkout.success', {}, 'AUTOSUCCESS_satchmo_checkout-success'),
                       )
