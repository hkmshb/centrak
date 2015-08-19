from django.conf.urls import patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^device-options/manufacturers/$', 'manufacturers', 
        name='manufacturers'),
    url(r'^device-options/manufacturers/delete(/(?P<id>[0-9]+))?', 
        'manufacturer_delete', name='manufacturer-delete'),
)
