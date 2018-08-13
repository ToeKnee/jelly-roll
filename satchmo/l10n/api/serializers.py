

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from satchmo.l10n.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'iso2_code', 'iso3_code', 'name', 'printable_name',
            'numcode', 'continent', 'admin_area', 'eu'
        )
        read_only_fields = (
            'iso2_code', 'iso3_code', 'name', 'printable_name',
            'numcode', 'continent', 'admin_area', 'eu'
        )
        depth = 2


class CountrySessionSerializer(serializers.Serializer):
    iso2_code = serializers.CharField(max_length=3)

    def validate_iso2_code(self, value):
        """
        Check that the currency is accepted
        """
        if Country.objects.filter(active=True, iso2_code=value).exists() is False:
            raise serializers.ValidationError(
                _("{value} is not an available country".format(value=value))
            )
        return value
