from django.conf.urls import patterns, include, url
from elco import urls as elco_urls



urlpatterns = patterns('',
    url(r'', include('main.urls')),
    url(r'', include('core.urls')),
    url(r'', include(elco_urls)),
    url(r'^enum/', include('enumeration.urls')),
)
