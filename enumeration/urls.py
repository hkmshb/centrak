from django.conf.urls import patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^device-options/manufacturers/$', 'manufacturers', 
        name='manufacturers'),
    url(r'^device-options/manufacturers/delete(/(?P<id>[0-9]+))?', 
        'manufacturer_delete', name='manufacturer-delete'),
                       
    url(r'^device-options/mobile-os/$', 'mobile_os', name='mobile-os'),
    url(r'^device-optinos/mobile-os/delete(/(?P<id>[0-9]+))?',
        'mobile_os_delete', name='mobile-os-delete'),
)
