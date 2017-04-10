from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import CurrencySerializer
from satchmo.currency.models import Currency


class CurrencyListAPIView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = CurrencySerializer

    def get_queryset(self):
        queryset = Currency.objects.all_accepted().order_by("-primary", "name")
        return queryset
