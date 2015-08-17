from django.conf.urls import patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^device-options/$', 'device_options', name='device-options')
)
