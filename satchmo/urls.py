from django.conf import settings
from django.contrib import admin

from satchmo.urls_base import urlpatterns as satchmopatterns

# discover all admin modules - if you override this for your
# own base URLs, you'll need to autodiscover there.
admin.autodiscover()

urlpatterns = getattr(settings, 'URLS', [])

urlpatterns += satchmopatterns
