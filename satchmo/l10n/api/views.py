from rest_framework.generics import ListAPIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
# Error 422 exists in a newer version of rest_framework, use it if
# it's available.
try:
    from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
except ImportError:
    HTTP_422_UNPROCESSABLE_ENTITY = 422
from rest_framework.views import APIView

from .serializers import CountrySerializer, CountrySessionSerializer
from satchmo.l10n.models import Country
from satchmo.l10n.utils import country_for_request


class CountryListAPIView(ListAPIView):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
    serializer_class = CountrySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Country.objects.filter(
            active=True).order_by("printable_name")
        return queryset


class CountrySessionAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Return the country for the request.
        """
        country_code = country_for_request(request)
        country = Country.objects.get(
            active=True,
            iso2_code=country_code
        )
        serializer = CountrySerializer(country)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Set the country in the session.
        """
        serializer = CountrySessionSerializer(data=request.data)
        if serializer.is_valid():
            # Save to session
            request.session["shipping_country"] = serializer.data["iso2_code"]
        else:
            return Response(serializer.errors, status=HTTP_422_UNPROCESSABLE_ENTITY)

        country = Country.objects.get(
            active=True,
            iso2_code=serializer.data["iso2_code"],
        )
        serializer = CountrySerializer(country)
        return Response(serializer.data)
