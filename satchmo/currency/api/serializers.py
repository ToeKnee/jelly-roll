from rest_framework import serializers

from satchmo.currency.models import (
    Currency,
    ExchangeRate,
)


class CurrencySerializer(serializers.ModelSerializer):
    latest_exchange_rate = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = (
            'iso_4217_code', 'name', 'symbol',
            'primary', 'accepted', 'latest_exchange_rate'
        )
        read_only_fields = (
            'iso_4217_code', 'name', 'symbol',
            'primary', 'accepted', 'latest_exchange_rate'
        )

    def get_latest_exchange_rate(self, obj):
        try:
            exr = obj.exchange_rates.latest()
        except ExchangeRate.DoesNotExist:
            return None
        else:
            return exr.rate
