from django.conf.urls import patterns, include, url



urlpatterns = patterns('',
    url(r'', include('main.urls')),
    url(r'^enum/', include('enumeration.urls')),
)
