==================
JellyRoll Change Log
==================

Version 0.12.0.12, 03 February, 2020
------------------------------
* Split item discount between items when creating PayPal Data

Version 0.12.0.11, 27 January, 2020
------------------------------
* Wishlist: Do not display wishlist items for inactive products
* Discount: Display correct date format

Version 0.12.0.10, 27 January, 2020
------------------------------
* Hotfix instead of release... :blush:

Version 0.12.0.9, 31 August, 2019
------------------------------
* PayPal: Change handling of payment created as sometimes the order
  number does not exist.


Version 0.12.0.8, 31 August, 2019
------------------------------
* PayPal: Change handling of payment created as sometimes the order
  number does not exist.
* Ingenico: Improve logging when verification fails

Version 0.12.0.7, 15 July, 2019
------------------------------
* Improve handling of unfulfilled order manager

Version 0.12.0.6, 08 July, 2019
------------------------------
* Revert - Improve handling of unfulfilled order manager

Version 0.12.0.5, 08 July, 2019
------------------------------
* Improve handling of unfulfilled order manager

Version 0.12.0.4, 24 June, 2019
------------------------------
* PayPal: Handle payment created.

Version 0.12.0.3, 12 June, 2019
------------------------------
* PayPal: Handle the order item discount.

Version 0.12.0.2, 11 June, 2019
------------------------------
* PayPal: Make sure we remove the discount from the sub_total when creating order.
* PayPal: Handle Risk Dispute

Version 0.12.0.1, 04 May, 2019
------------------------------
* Update max Django version

Version 0.12.0.0, 04 May, 2019
------------------------------
* Give products a standard `unit_price`. Only look for discount
  prices if quantity is greater than one.
* Remove multi-site support
* Remove database level translations

Version 0.11.3.0, 25 March, 2019
------------------------------
* Black code format
* Cache currency_for_request for the request

Version 0.11.2.3, 17 December, 2018
------------------------------
* Fix double currency conversion of discounts

Version 0.11.2.2, 25 September, 2018
------------------------------
* Fix recalculate totals

Version 0.11.2.1, 25 September, 2018
------------------------------
* Fix Paypal Webhook - already processed
* Fix order history page

Version 0.11.2.0, 24 September, 2018
------------------------------
* Reduce Brand pages
* Order Status updates
* Remove custom slugify

Version 0.11.1.5, 01 September, 2018
------------------------------
* Fix adding more products to cart than stock available

Version 0.11.1.4, 28 August, 2018
------------------------------
* Fix encoding when reading request.body in webhook

Version 0.11.1.3, 28 August, 2018
------------------------------
* Make sure add_status sets the current status to the latest order status

Version 0.11.1.2, 25 August, 2018
------------------------------
* 404 When order can't be found on payment-create
* Make sure we pass payment info to payment-execute

Version 0.11.1.1, 25 August, 2018
------------------------------
* Replace straight API calls with PayPalRestSDK

Version 0.11.1.0, 25 August, 2018
------------------------------
* Change from PayPal IPN to PayPal API

Version 0.11.0.7, 21 August, 2018
------------------------------
* Fix admin settings
* Add accepted stage to PayPal IPN

Version 0.11.0.6, 21 August, 2018
------------------------------
* Fix PayPal IPN

Version 0.11.0.5, 21 August, 2018
------------------------------
* Handle AddressNotFoundError when using geoip
* Add URL to payment success error email
* Empty shipping migrations
  Covered by tieredweightzone migrations, split during Django 2.1 upgrade
* Add obj=None to ExchangeRateInline has_add_permission
* Fix calculating of currency converted discounts

Version 0.11.0.4, 20 August, 2018
------------------------------
* Don't re-encode shipping description

Version 0.11.0.3, 20 August, 2018
------------------------------
* Redirect to order status if we can't find the order in the request

Version 0.11.0.2, 20 August, 2018
------------------------------
* Improve Order.objects.from_request
* Raise 404 for bad_or_missing

Version 0.11.0.1, 20 August, 2018
------------------------------
* Parse JSON request body in six fulfilment module

Version 0.11.0.0, 20 August, 2018
------------------------------
* Upgrade to Python 3
* Upgrade to Django 2.1

Version 0.10.3.5, 11 Jun, 2018
------------------------------
* Update fixer.io API
* Add ECB (European Central Bank) exchange rate provider

Version 0.10.3.4, 31 May, 2018
------------------------------
* Improved MPN in product feed
* Added availability to product feed
* Added additional images to product feed

Version 0.10.3.3, 31 May, 2018
------------------------------
* Add MPN to product feed

Version 0.10.3.2, 16 April, 2018
-------------------------------
* PayPal checkout deadlock fixes

Version 0.10.3.1, 16 April, 2018
-------------------------------
* Currency conversion only applied once to 'other' currency prices

Version 0.10.3.0, 5 April, 2018
-------------------------------
* Add other currency prices to full product page

Version 0.10.2.3, 21 Feb, 2018
-------------------------------
* Fix OrderPayment admin currency

Version 0.10.2.2, 7 Feb, 2018
-------------------------------
* Default payment method

Version 0.10.2.1, 6 Feb, 2018
-------------------------------
* Add appropriate indexes to l10n models

Version 0.10.2.0, 5 Feb, 2018
-------------------------------
* Add all prices to product page context

Version 0.10.1.1, 5 Feb, 2018
-------------------------------
* Add missing code for cheapest shipping to base cart

Version 0.10.1.0, 3 Feb, 2018
-------------------------------
* Add cheapest shipping to base cart

Version 0.10.0.0, 3 Feb, 2018
-------------------------------
* Add mult-currency support

Version 0.9.7.8, 11 May, 2017
-------------------------------
* Ingenico handle unicode characters in process views

Version 0.9.7.7, 9 May, 2017
-------------------------------
* Ingenico handle unicode characters in shasign

Version 0.9.7.6, 28 April, 2017
-------------------------------
* Ingenico handle payment deleted like a refund

Version 0.9.7.5, 27 April, 2017
-------------------------------
* Ingenico improve handling visiting accepted page after processing order

Version 0.9.7.4, 27 April, 2017
-------------------------------
* Ingenico handle random case sensitivity of return values

Version 0.9.7.3, 26 April, 2017
-------------------------------
* Ingenico SHASIGN - handle lower case keys properly
* Ingenico SHASIGN - handle empty values properly

Version 0.9.7.2, 26 April, 2017
-------------------------------
* Add Alias Usage

Version 0.9.7.1, 26 April, 2017
-------------------------------
* Fix Alias length

Version 0.9.7, 26 April, 2017
-----------------------------
* Add Ingenico payment module

Version 0.9.6, 26 Dec, 2016
---------------------------
* Fix early notification issue

Version 0.9.5, 6 Dec, 2016
--------------------------
* Status admin, list display notify and display
* Update email images to be background-images
* Send order status email on status create

Version 0.9.4, 3 Dec, 2016
--------------------------
 * Add order status emails
 * Add html emails
 * Use https://github.com/leemunroe/responsive-html-email-template as a basis for HTML emails

Version 0.9.3,
------------------------------
* Fix caching of translations
* Fix pycrypto requirement

Version 0.9.2, 22 August, 2016
------------------------------
 * Improve filtering of product list admin
 * Make stock quantities editable in the product list admin
 * Add missing requirements: requests, httmock
 * Make "six" fulfilment API test portable

Version 0.9.1, 15 August, 2016
---------------------------
 * Add CarrierTranslationFactory to CarrierFactory to fix issue with debugging tests

Version 0.9, 15 August, 2016
---------------------------
 * A sudden and unexpected return to version numbers, changelogs and
   good branching practices.
 * Add shipping estimates (to tieredweightzone)
 * Make optional apps required
 * Refactor tests (still more to do)
 * Remove thumbnail app

Version 0.8, November 25, 2008
-----------------------------
 * Add USPS shipping module
 * Converted to using newforms admin
 * Made country validation of post code and territories/states more robust
 * Added Protx payment support
 * New config setting to hide translation fields
 * Refactored payment code to be more modular
 * Change a time stamp field name for Oracle compatability
 * Added support for brands
 * New shuffle filter
 * Multi-site support
 * Added Italian & Hebrew translation
 * Migrated to new django comments functionality. Remove the need for comment_utils
 * Move admin to use nfa and rest of Satchmo now compatible with django 1.0
 * Removed all standalone satchmo settings from settings.py and local_settings.py, moving them
   to a dictionary.  This allows for explicit defaults and for easier integration with other apps.
 * Moved all order methods, classes and views into the satchmo.shop application from Contact
 * Fixed circular imports in several apps.
 * New configuration feature in payment section, allowing shop owners to be notified by email
   when they have a new sale.
 * Refactor of emailing on order completion, now uses signals, simplifying payment modules.
 * New optional app "satchmo.upsell" which allows product upselling on product detail pages.
 * New signals in get_qty_price methods of products, allowing code to manipulate the price returned
   by the function.  Example code using these signals is at satchmo.contrib.cartqty_discounts,
   which modifies the qty_discount method to calculate the discount based on the total number of items
   in the cart, rather than the total amount of the lineitem.
 * Improved inheritance of detail_producttype.html pages, which no longer need to duplicate as much of
   the code of base_product.html, allowing for easier addition of features to the product detail pages.
 * New most popular, best sellers and recently added views
 * New tiered shipping module based on quantity
 * New Fedex shipping module
 * New configuration option to force login for checkout
 * Refactored base template layout to be more extensible
 * Refactored the login and signup code to make it more extensible
 * Improved performance of price lookups
 * Recurring billing support for Authorize.net
 * New Purchase Order payment module

Version 0.7, May 26, 2008
-------------------------
 * Added config files to make rpm creation easier
 * German translation
 * New capability to choose the translation language
 * COD payment module
 * Category code cleanup
 * Highlight active category in the menu
 * Install documentation cleanup
 * New feature to manage translations of all parts of Satchmo content
 * Ability to add images to categories & override category sort order
 * Improvements to CustomProduct to make it more broadly useable
 * Currency displayed using the chosen locale
 * Documented creation of custom payment modules
 * Creation of new templatetags (product_category_siblings and product_images)
 * Created new Shipping Module, 'Tiered', allowing multiple carriers and variable pricing by cart total.
 * Added cybersource payment module
 * New config values to display featured products randomly
 * Increased length of Contact phonenumber to work internationally
 * Added shipping countries directly to Shop - allowing the shops to specify legal countries for shipping.
 * Updated google analytics to new code, with an optional fallback to the old urchin.js
 * Added new Tax module "Area", which calculates taxes based on country or state.
 * Updated discount system to track which discounts were applied to which line items.
 * Add weight and dimension unit info to the product model.
 * Provide integration for UPS online tools.
 * New sku model field
 * New gift certificate capability.
 * Fixed New Zealand states/region info in l10n data
 * Improvements to tax calc code
 * Updated swedish translation
 * Improve checks to make sure dupe emails are not used by accounts
 * Fixed a bug with PDF generation in windows
 * Improved product export capability to support categories
 * Added Brazilian Portuguese translation
 * Added a subscription product
 * Cleaned up breadcrumbs to make it easier to modify via css
 * Removed storage of ccv field in database
 * Actually keep track of items when they are sold
 * Swedish and German translation updates
 * Can now prevent someone from purchasing an item that is out of stock
 * Google feed support
 * New Bulgarian translation
 * Korean translation
 * Recently viewed items support
 * Wishlist support
 * UI improvements to the admin site
 * Added some javascript to disable shipping address fields if "same shipping and billing address are used"
 * SEO optimizations to templates
 * Performance improvements when using Configurable Products
 * Fix some unicode issues with some of the shipping and payment processing backends
 * Trustcommerce bug fixes
 * Updated documentation to use sphinx
 * Fixed some bugs in pdf generation
 * Made pdf logo selection part of the configuration settings

Version 0.6, October 30, 2007
----------------
 * Removed dependency on Webda and added new l10n models
 * Added capability to rate and review products
 * Improved capabilities for users to manage their account information
 * Creation of a simple inventory management interface
 * Multiple bug fixes and code cleanups
 * New configuration option to allow user to set image upload directory name
 * Improved error handling for loading data
 * Allow manual product ordering in a category
 * Remove most custom settings from local_settings.py, instead using the satchmo.configuration app
 * Added a cache manager
 * Added TrustCommerce as a processing module
 * New downloadable product type
 * New custom product type
 * Added Swedish translation

Version 0.5, August 22, 2007
----------------------------
 * First official package launch
