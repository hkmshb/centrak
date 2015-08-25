from django.conf.urls import patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^device-options/manufacturers/$', 'manufacturers', name='manufacturers'),
    url(r'^device-options/manufacturers/update/(?P<id>[0-9]+)',
        'manufacturer_update', name='manufacturer-update'),
    url(r'^device-options/manufacturers/delete(/(?P<id>[0-9]+))?', 
        'manufacturer_delete', name='manufacturer-delete'),
                       
    url(r'^device-options/mobile-os/$', 'mobile_os', name='mobile-os'),
    url(r'^device-options/mobile-os/update/(?P<id>[0-9]+)',
        'mobile_os_update', name='mobile-os-update'),
    url(r'^device-optinos/mobile-os/delete(/(?P<id>[0-9]+))?',
        'mobile_os_delete', name='mobile-os-delete'),
)
