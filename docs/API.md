# Jelly Roll API

This document describes the API for developers wishing to implement a
client for the Jelly Roll shop.


## Currency

### LIST

    GET: /SHOP_BASE/api/currency/

Returns a list of currencies accepted by the system.


### Session

    GET: /SHOP_BASE/api/currency/session/

Return the currency in use for the current session.

    POST: /SHOP_BASE/api/currency/session/
    Fields: iso_4217_code*
    * required fields

Set the currency for the current session. The `iso_4217_code` (3 letter
currency code) is required and it must be one of the accepted
currencies.
