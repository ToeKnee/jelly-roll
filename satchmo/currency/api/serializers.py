from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from satchmo.currency.models import Currency, ExchangeRate


class CurrencySerializer(serializers.ModelSerializer):
    latest_exchange_rate = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = (
            "iso_4217_code",
            "name",
            "symbol",
            "primary",
            "accepted",
            "latest_exchange_rate",
        )
        read_only_fields = (
            "iso_4217_code",
            "name",
            "symbol",
            "primary",
            "accepted",
            "latest_exchange_rate",
        )

    def get_latest_exchange_rate(self, obj):
        try:
            exr = obj.exchange_rates.latest()
        except ExchangeRate.DoesNotExist:
            return None
        else:
            return exr.rate


class CurrencySessionSerializer(serializers.Serializer):
    iso_4217_code = serializers.CharField(max_length=3)

    def validate_iso_4217_code(self, value):
        """
        Check that the currency is accepted
        """
        if (
            Currency.objects.all_accepted().filter(iso_4217_code=value).exists()
            is False
        ):
            raise serializers.ValidationError(
                _("{value} is not an accepted currency".format(value=value))
            )
        return value
