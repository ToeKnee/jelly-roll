from .utils import shasign

from django import forms
from satchmo.configuration.functions import config_get_group

payment_module = config_get_group("PAYMENT_INGENICO")


class IngenicoForm(forms.Form):
    PSPID = forms.CharField(required=True, widget=forms.HiddenInput())
    ORDERID = forms.IntegerField(required=True, widget=forms.HiddenInput())
    AMOUNT = forms.CharField(required=True, widget=forms.HiddenInput())
    CURRENCY = forms.CharField(required=True, widget=forms.HiddenInput())
    CN = forms.CharField(required=True, widget=forms.HiddenInput())
    EMAIL = forms.EmailField(required=True, widget=forms.HiddenInput())
    OWNERADDRESS = forms.CharField(required=False, widget=forms.HiddenInput())
    OWNERZIP = forms.CharField(required=False, widget=forms.HiddenInput())
    OWNERTOWN = forms.CharField(required=False, widget=forms.HiddenInput())
    OWNERCTY = forms.CharField(required=False, widget=forms.HiddenInput())  # Country
    OWNERTELNO = forms.CharField(required=False, widget=forms.HiddenInput())

    # Generate this field
    SHASIGN = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(IngenicoForm, self).__init__(*args, **kwargs)

        # If Alias / Tokenisation is used
        if payment_module.ALIAS.value:
            self.fields["ALIAS"] = forms.CharField(
                required=True, widget=forms.HiddenInput()
            )
            self.fields["ALIASUSAGE"] = forms.CharField(
                required=True, widget=forms.HiddenInput()
            )

        # Generate the SHASIGN
        self.data["SHASIGN"] = shasign(self.data)
