from rest_framework.generics import ListAPIView
from rest_framework.response import Response

# Error 422 exists in a newer version of rest_framework, use it if
# it's available.
try:
    from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
except ImportError:
    HTTP_422_UNPROCESSABLE_ENTITY = 422
from rest_framework.views import APIView

from .serializers import CurrencySerializer, CurrencySessionSerializer
from satchmo.currency.models import Currency
from satchmo.currency.utils import currency_for_request
from satchmo.payment.utils import update_orderitems
from satchmo.shop.models import Cart, Order


class CurrencyListAPIView(ListAPIView):
    serializer_class = CurrencySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Currency.objects.all_accepted().order_by("-primary", "name")
        return queryset


class CurrencySessionAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Return the currency for the request.
        """
        currency_code = currency_for_request(request)
        currency = Currency.objects.all_accepted().get(iso_4217_code=currency_code)
        serializer = CurrencySerializer(currency)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Set the currency in the session.
        """
        serializer = CurrencySessionSerializer(data=request.data)
        if serializer.is_valid():
            currency_code = serializer.data["iso_4217_code"]
            currency = Currency.objects.all_accepted().get(iso_4217_code=currency_code)

            # Save to session
            request.session["currency_code"] = currency_code

            # Update current cart
            cart = Cart.objects.from_request(request)
            if isinstance(cart, Cart):
                cart.currency = currency
                cart.save()

            # Update current order
            try:
                order = Order.objects.from_request(request)
            except Order.DoesNotExist:
                pass
            else:
                if order.frozen is False:
                    order.currency = currency
                    order.save()
                    update_orderitems(order, cart, update=True)

        else:
            return Response(serializer.errors, status=HTTP_422_UNPROCESSABLE_ENTITY)

        currency = Currency.objects.all_accepted().get(
            iso_4217_code=serializer.data["iso_4217_code"]
        )
        serializer = CurrencySerializer(currency)
        return Response(serializer.data)
