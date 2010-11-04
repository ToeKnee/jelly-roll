from django.db import models
from satchmo.configuration import config_value_safe, config_choice_values
from satchmo.payment.config import credit_choices, labelled_payment_choices
from south.modelsinspector import add_introspection_rules

class CreditChoiceCharField(models.CharField):

    def __init__(self, choices="__DYNAMIC__", *args, **kwargs):
        if choices == "__DYNAMIC__":
            kwargs['choices'] = credit_choices()

        super(CreditChoiceCharField, self).__init__(*args, **kwargs)
add_introspection_rules([], ["^satchmo\.payment\.fields\.CreditChoiceCharField"])

class PaymentChoiceCharField(models.CharField):
    
    def __init__(self, choices="__DYNAMIC__", *args, **kwargs):
        if choices == "__DYNAMIC__":
            kwargs['choices'] = labelled_payment_choices()
                    
        super(PaymentChoiceCharField, self).__init__(*args, **kwargs)
add_introspection_rules([], ["^satchmo\.payment\.fields\.PaymentChoiceCharField"])
