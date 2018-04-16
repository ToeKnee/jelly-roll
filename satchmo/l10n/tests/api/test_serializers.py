

from django.test import TestCase

from satchmo.l10n.api.serializers import CountrySerializer, CountrySessionSerializer
from satchmo.l10n.factories import UKFactory


class CountrySerializerTest(TestCase):
    def test_read_fields(self):
        country = UKFactory()
        country.active = True
        country.save()
        serializer = CountrySerializer(country)
        self.assertEqual(serializer.data["iso2_code"].encode("utf-8"), country.iso2_code.encode("utf-8"))
        self.assertEqual(serializer.data["iso3_code"].encode("utf-8"), country.iso3_code.encode("utf-8"))
        self.assertEqual(serializer.data["name"], country.name)
        self.assertEqual(serializer.data["printable_name"], country.printable_name)
        self.assertEqual(serializer.data["numcode"], country.numcode)
        self.assertEqual(serializer.data["continent"], {
            "id": country.continent.id,
            "code": country.continent.code,
            "name": country.continent.name,
        })
        self.assertEqual(serializer.data["admin_area"], country.admin_area)
        self.assertEqual(serializer.data["eu"], country.eu)


class CountrySessionSerializerTest(TestCase):
    def test_read_fields(self):
        country = UKFactory()
        serializer = CountrySessionSerializer(country)

        self.assertEqual(serializer.data["iso2_code"], country.iso2_code)
        self.assertEqual(len(list(serializer.data.keys())), 1)

    def test_validate__correct(self):
        country = UKFactory()

        data = {"iso2_code": country.iso2_code}
        serializer = CountrySessionSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_get__country_doesnt_exist(self):
        data = {"iso2_code": "ZZ"}
        serializer = CountrySessionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors,
            {'iso2_code': ["ZZ is not an available country"]}
        )
