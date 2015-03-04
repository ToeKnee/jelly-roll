from django.conf.urls import include, patterns, url

urlpatterns = patterns(
    '',

    url(r'^six/', include('satchmo.fulfilment.modules.six.urls'))
)
