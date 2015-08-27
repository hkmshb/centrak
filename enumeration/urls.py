from django.conf.urls import patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^devices/$', 'devices', name='devices'),
    url(r'^devices/create$', 'manage_device', name='device-insert'),
    url(r'^devices/update/(?P<id>[0-9]+)', 'manage_device', name='device-update'),
    url(r'^devices/delete(/(?P<id>[0-9]+))?', 'delete_device', name='device-delete'),
                       
    url(r'^device-options/manufacturers/$', 'manufacturers', name='manufacturers'),
    url(r'^device-options/manufacturers/update/(?P<id>[0-9]+)',
        'manufacturer_update', name='manufacturer-update'),
    url(r'^device-options/manufacturers/delete(/(?P<id>[0-9]+))?', 
        'manufacturer_delete', name='manufacturer-delete'),
                       
    url(r'^device-options/mobile-os/$', 'mobile_os', name='mobile-os'),
    url(r'^device-options/mobile-os/update/(?P<id>[0-9]+)',
        'mobile_os_update', name='mobile-os-update'),
    url(r'^device-options/mobile-os/delete(/(?P<id>[0-9]+))?',
        'mobile_os_delete', name='mobile-os-delete'),
)
